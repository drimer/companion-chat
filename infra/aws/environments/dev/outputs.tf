output "conversations_table_name" {
  description = "Name of the DynamoDB conversations table"
  value       = module.db.conversations_table_name
}

output "conversations_table_arn" {
  description = "ARN of the DynamoDB conversations table"
  value       = module.db.conversations_table_arn
}

output "users_table_name" {
  description = "Name of the DynamoDB users table"
  value       = module.db.users_table_name
}

output "users_table_arn" {
  description = "ARN of the DynamoDB users table"
  value       = module.db.users_table_arn
}

output "lambda_function_name" {
  description = "Name of the conversations Lambda function"
  value       = module.conversations_lambda.lambda_function_name
}

output "lambda_function_arn" {
  description = "ARN of the conversations Lambda function"
  value       = module.conversations_lambda.lambda_function_arn
}

output "lambda_deployments_bucket" {
  description = "S3 bucket used for Lambda deployment packages"
  value       = module.conversations_lambda.lambda_deployments_bucket
}

output "lambda_deployments_bucket_arn" {
  description = "ARN of the S3 bucket used for Lambda deployment packages"
  value       = module.conversations_lambda.lambda_deployments_bucket_arn
}

output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = module.api_gateway.api_gateway_url
}

output "api_gateway_id" {
  description = "ID of the API Gateway"
  value       = module.api_gateway.api_gateway_id
}

output "cognito_user_pool_id" {
  description = "ID of the Cognito user pool"
  value       = module.cognito.user_pool_id
}

output "cognito_user_pool_arn" {
  description = "ARN of the Cognito user pool"
  value       = module.cognito.user_pool_arn
}
