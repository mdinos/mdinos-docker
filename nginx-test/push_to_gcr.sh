#!/usr/bin/env bash

set -xe

docker build -t nginx-test:latest .
export PROJECT_ID="$(gcloud config get-value project -q)"
gcloud auth configure-docker
docker tag nginx-test:latest "gcr.io/${PROJECT_ID}/nginx-test:latest"
docker push "gcr.io/${PROJECT_ID}/nginx-test:latest"

IMAGE_NAME=$(gcloud container images list | grep 'nginx-test' | awk '{print $1}')
LTS_TAG=$(gcloud container images list-tags $IMAGE_NAME | grep 'latest' | awk '{print $1}')

echo LTS_TAG=$LTS_TAG
