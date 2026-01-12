output "user_pool_id" {
  value       = aws_cognito_user_pool.this.id
  description = "ID of the Cognito user pool"
}

output "user_pool_arn" {
  value       = aws_cognito_user_pool.this.arn
  description = "ARN of the Cognito user pool"
}

output "user_pool_client_id" {
  value       = aws_cognito_user_pool_client.app.id
  description = "Client ID for the default app client"
}
