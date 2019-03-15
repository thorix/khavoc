#!/bin/bash

containername=khavoc

if [[ $(docker ps -a | grep $containername) ]]; then
  docker stop $containername; docker rm $containername
fi

docker pull nginx:alpine
docker run --name $containername \
  -p 80:80 \
  -v $(pwd)/www:/config/www:ro \
  -v $(pwd)/nginx.default.conf:/etc/nginx/conf.d/default.conf:ro \
  -d nginx:alpine

