#!/bin/bash

./gradlew clean build buildZip
sam package --template-file infra/cf-stack.yml --output-template-file packaged.yml --s3-bucket cf-templates-1tytu2v0l6bsz-eu-west-2
sam deploy --template-file packaged.yml --stack-name companion-chat-stack --capabilities CAPABILITY_IAM