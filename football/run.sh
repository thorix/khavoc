#!/bin/bash

WEBHOOK_URL=$1
WEBHOOK_AUTH=$2
docker build -t khavoc .

docker stop khavoc
docker rm khavoc
docker run \
  -d \
  --name khavok \
  --privileged \
  --restart unless-stopped \
  -e WEBHOOK_URL=${WEBHOOK_URL} \
  -e WEBHOOK_AUTH_TOKEN=${WEBHOOK_AUTH} \
  khavoc
