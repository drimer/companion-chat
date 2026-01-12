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

output "issuer_url" {
  value       = aws_cognito_user_pool.this.endpoint
  description = "Issuer URL for the Cognito user pool"
}

output "user_pool_domain" {
  value       = aws_cognito_user_pool_domain.this.domain
  description = "Domain prefix assigned to the hosted UI"
}

output "user_pool_hosted_ui_url" {
  value       = "https://${aws_cognito_user_pool_domain.this.domain}.auth.${data.aws_region.current.name}.amazoncognito.com"
  description = "Base URL for the Cognito hosted UI"
}