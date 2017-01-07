#!/bin/bash

DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONTAINER_NAME='church-mongo'
docker run -it --rm --name ${CONTAINER_NAME} -p 27017:27017 -v ${DIR}/db:/data/db mongo
