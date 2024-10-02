#!/bin/bash

./gradlew clean build buildZip
sam package --template-file infra/cicd-stack.yml --output-template-file cicd-stack-packaged.yml --s3-bucket cf-templates-1tytu2v0l6bsz-eu-west-2
sam deploy --template-file cicd-stack-packaged.yml --stack-name companion-chat-cicd-stack --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND