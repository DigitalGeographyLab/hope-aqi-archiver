#!/bin/bash

set -ex

TAG=${1}
USER='hellej'
DOCKER_IMAGE=${USER}/hope-aqi-archiver:${TAG}
DOCKER_IMAGE_LATEST=${USER}/hope-aqi-archiver:latest

docker build -t ${DOCKER_IMAGE} .

docker tag ${DOCKER_IMAGE} ${DOCKER_IMAGE_LATEST}
docker login
docker push ${DOCKER_IMAGE_LATEST}
