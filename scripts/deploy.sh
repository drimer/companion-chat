#!/bin/bash

set -x 

terraform -chdir=infra/aws/environments/dev init
terraform -chdir=infra/aws/environments/dev workspace select -or-create dev
terraform -chdir=infra/aws/environments/dev plan -out=tfplan
terraform -chdir=infra/aws/environments/dev apply tfplan
