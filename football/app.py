import RPi.GPIO as GPIO
import time
import sys
import os
import requests

ON = False
OFF = True

class State:
    def __init__(self, name, initial_value):
        print "Initialize", name, "to", initial_value
        self.name = name
        self.value = initial_value
        self.listeners = []

    def update(self, value):
        if self.value != value:
            #print "Update", self.name, "to", value
            self.value = value
            for l in self.listeners:
                l(value)

    def listen(self, listener):
        listener(self.value)
        self.listeners += [listener]

def mergeState(a, b, name, fn):
    res = State(name, fn(a.value, b.value))
    a.listen(lambda v: res.update(fn(v, b.value)))
    b.listen(lambda v: res.update(fn(a.value, v)))
    return res

def fromSwitch(value):
    if value == 0:
        return False
    else:
        return True

def switchState(channel, name):
    GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def read():
        time.sleep(0.1) #Allow the signal to change
        r = fromSwitch(GPIO.input(channel))
        print "Read", name, r
        return r

    res = State(name, read())
    def onToggle(ch):
        res.update(read())

    GPIO.add_event_detect(channel, GPIO.BOTH, callback=onToggle, bouncetime=300)

    return res

def toLed(v):
    if v:
        return ON
    else:
        return OFF

def outputState(channel, name, trigger):
    GPIO.setup(channel, GPIO.OUT)
    def onUpdate(v):
        print "Led", name, "to", v
        GPIO.output(channel, toLed(v))
    trigger.listen(onUpdate)

def reversedOutputState(channel, name, trigger):
    GPIO.setup(channel, GPIO.OUT)
    def onUpdate(v):
        print "Led", name, "to", v
        GPIO.output(channel, toLed(not v))
    trigger.listen(onUpdate)

def maybeDoRelease(doit):
    if doit:
        print "Doing the publish !!!"
        URL = os.environ['WEBHOOK_URL']
        TOKEN = os.environ['WEBHOOK_AUTH_TOKEN']
        headers = {'X-Auth': TOKEN}
        r = requests.delete(url=URL, headers=headers)
        data = r.json()
        print data

def andState(a, b):
    return mergeState(a, b, a.name + "&" + b.name, lambda a, b: a and b)

def orState(a, b):
    return mergeState(a, b, a.name + "|" + b.name, lambda a, b: a or b)

def main():
    GPIO.setmode(GPIO.BCM)

    key1 = switchState(18, "left_key")
    key2 = switchState(7, "right_key")

    switch1 = switchState(14, "left_switch")
    switch2 = switchState(25, "right_switch")

    clock = State("clock", False)
    on_boot = State("on_boot", True)

    outputState(15, "key1", orState(on_boot, andState(key1, orState(switch1, clock))))
    outputState(8, "key2", orState(on_boot, andState(key2, orState(switch2, clock))))

    left = andState(key1, switch1)
    right = andState(key2, switch2)

    ready = andState(left, right)

    reversedOutputState(24, "button", orState(on_boot, ready))

    button = switchState(23, "button")

    release = andState(ready, button)

    release.listen(maybeDoRelease)

    i = 0

    while True:
        time.sleep(0.25)
        clock.update(not clock.value)
        if i >= 4:
            on_boot.update(False)
        i += 1

if __name__=='__main__':
    try:
        main()
    except:
        GPIO.cleanup()
        exit(1)
