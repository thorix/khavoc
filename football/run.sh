#!/bin/bash

WEBHOOK_URL=$1
WEBHOOK_AUTH=$2
docker build -t khavok .

docker stop khavok
docker rm khavok
docker run \
  -d \
  --name khavok \
  --privileged \
  --restart unless-stopped \
  -e WEBHOOK_URL=${WEBHOOK_URL} \
  -e WEBHOOK_AUTH_TOKEN=${WEBHOOK_AUTH} \
  khavok
