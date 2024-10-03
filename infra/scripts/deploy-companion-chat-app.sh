#!/bin/bash

set -x

./gradlew clean build buildZip
sam package --template-file infra/cc-app-stack.yml --output-template-file packaged.yml --s3-bucket cf-templates-1tytu2v0l6bsz-eu-west-2
sam deploy --template-file packaged.yml --stack-name ${ENVIRONMENT}-companion-chat-stack --parameter-overrides Environment=${ENVIRONMENT} --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND