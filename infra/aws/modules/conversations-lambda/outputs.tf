output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.conversations.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.conversations.arn
}

output "lambda_deployments_bucket" {
  description = "S3 bucket used for Lambda deployment packages"
  value       = aws_s3_bucket.lambda_deployments.bucket
}

output "lambda_deployments_bucket_arn" {
  description = "ARN of the S3 bucket used for Lambda deployment packages"
  value       = aws_s3_bucket.lambda_deployments.arn
}