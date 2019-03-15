#!/bin/bash

DOMAIN=${1}

kubeless function delete khavoc
kubeless function deploy khavoc \
  --runtime go1.10 \
  --from-file khavoc.go \
  --dependencies Gopkg.toml \
  --handler khavoc.Handler

kubeless trigger http delete khavoc
kubeless trigger http create khavoc \
  --function-name khavoc \
  --path khavoc \
  --hostname ${DOMAIN}
