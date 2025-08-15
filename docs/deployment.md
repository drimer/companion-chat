# Deployment Guide

## Manual Steps required for a brand new deployment in AWS

1. **Create S3 bucket for Terraform state**:
   ```bash
   aws s3 mb s3://companion-chat-terraform-state
   ```

2. **Create IAM user for Terraform** with the following policy:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "VisualEditor0",
         "Effect": "Allow",
         "Action": [
           "s3:*",
           "dynamodb:*",
           "lambda:*",
           "iam:*",
           "logs:*",
           "apigateway:*"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

3. **Deploy to AWS using GitHub Actions**

4. **Update OpenAI API Key after deployment**:
   The Lambda function is deployed with a dummy OpenAI API key. You need to update it manually via AWS Console:
   
   - Go to AWS Lambda Console
   - Find the `conversations-lambda` function (name will be like: `companion-chat-dev-chat-conversations-lambda`)
   - Go to Configuration → Environment variables
   - Update `OPENAI_API_KEY` with your real API key
   - Click "Save"

## Automated Deployment

Deployments are automated with GitHub Actions. The pipeline:
1. Runs all tests (unit, integration, e2e)
2. Builds deployment package
3. Deploys to AWS using Terraform

### Terraform Validation Commands

For validation and troubleshooting purposes only. **Actual deployment should always be done via GitHub Actions.**

```bash
# Validate deployment configuration
terraform -chdir=infra/aws/environments/dev plan

# Initialize if needed
terraform -chdir=infra/aws/environments/dev init
```

## Infrastructure Architecture

The deployment creates:
- **AWS Lambda**: Serverless function hosting the FastAPI application
- **DynamoDB**: NoSQL database for conversation storage
- **API Gateway**: REST API frontend with CORS support
- **S3**: Storage for Lambda deployment packages (handles 70MB+ packages)
- **CloudWatch**: Logging and monitoring

## Environment Configuration

### Development Environment
- API Gateway: `https://uycxfk6mv4.execute-api.eu-west-2.amazonaws.com/dev`
- Lambda Function: `companion-chat-dev-chat-conversations-lambda`
- DynamoDB Table: `companion-chat-dev-conversations`
