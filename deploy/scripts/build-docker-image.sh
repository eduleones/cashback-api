#!/bin/bash

APP_NAME=$1
DOCKERFILE_NAME=Dockerfile
APP_VERSION=$(cat VERSION)
UID=$(id -u)
GID=$(id -g)


echo "Building image for APP_NAME=$APP_NAME, DOCKERFILE_NAME=$DOCKERFILE_NAME, VERSION=$APP_VERSION, UID=$UID, GID=$GID..." \
    && docker build -t $APP_NAME:$APP_VERSION --pull --no-cache --build-arg UID=$UID --build-arg GID=$GID -f $DOCKERFILE_NAME . \
    && echo "Successfully built image for APP_NAME=$APP_NAME, DOCKERFILE_NAME=$DOCKERFILE_NAME, VERSION=$APP_VERSION, UID=$UID, GID=$GID."

IMAGE_ID=$(docker images --filter reference=$APP_NAME | grep $APP_VERSION | awk '{print $3}')

echo "Tagging IMAGE_ID=${IMAGE_ID} as latest..." \
    && docker tag $IMAGE_ID $APP_NAME:latest \
    && echo "IMAGE_ID=${IMAGE_ID} successfully tagged as latest."
