#!/usr/bin/env bash

set -xe

$(aws-profile -p marcus-superuser aws ecr get-login --no-include-email --region eu-north-1)
docker build -t mdinos-images:rs-api-latest .
docker tag mdinos-images:rs-api-latest 474307705618.dkr.ecr.eu-north-1.amazonaws.com/mdinos-images:rs-api-latest
docker push 474307705618.dkr.ecr.eu-north-1.amazonaws.com/mdinos-images:rs-api-latest