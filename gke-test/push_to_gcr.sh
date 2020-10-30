#!/usr/bin/env bash

set -xe

docker build -t gke-test:latest .
export PROJECT_ID="$(gcloud config get-value project -q)"
gcloud auth configure-docker
docker tag gke-test:latest "gcr.io/${PROJECT_ID}/gke-test:latest"
docker push "gcr.io/${PROJECT_ID}/gke-test:latest"

