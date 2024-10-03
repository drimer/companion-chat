# companion-chat

Companion Chat app - for all your needs

# Manual steps needed before using any script

1. Create an S3 bucket for storing SAM templates.
   1.1. Replace the bucket name in the script `./infra/scripts/deploy-companion-api-lambda.sh`
2. Create a service roles for CodeBuild that allows the following:
   ```
   "iam:*",
   "s3:*",
   "cloudformation:*",
   "lambda:*",
   "logs:*",
   "apigateway:*",
   "dynamodb:*"
   ```

# Processes requiring manual intervention

## Changes to the pipeline config

In order to apply changes to the pipeline config, run the script
`./infra/scripts/deploy-cicd-setup.sh`.

## Notes to self

Things to add to CF template:

- CodeBuild role(s)
- CodeBuild project
- CodePipeline role(s)
- CodePipeline pipeline

# Tips for faster development

To deploy the app to a sandbox, without having to commit and push:

```shell
ENVIRONMENT=aaj ./infra/scripts/deploy-companion-chat-app.sh
```