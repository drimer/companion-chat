#!/bin/bash

set -x 

terraform -chdir=infra/aws/environments/dev init
terraform -chdir=infra/aws/environments/dev workspace select -or-create dev
terraform -chdir=infra/aws/environments/dev plan -var="openai_api_key=$OPENAI_API_KEY" -var="cors_origins=$CORS_ORIGINS" -out=tfplan
terraform -chdir=infra/aws/environments/dev apply tfplan
