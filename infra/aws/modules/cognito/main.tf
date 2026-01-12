locals {
  user_pool_name          = join("-", compact(tolist([var.group, var.environment, var.scope, "users"])))
  user_pool_client_name   = "${local.user_pool_name}-client"
  user_pool_domain_prefix = var.domain_prefix != "" ? var.domain_prefix : replace(local.user_pool_name, "_", "-")
}

data "aws_region" "current" {}

resource "aws_cognito_user_pool" "this" {
  name                       = local.user_pool_name
  auto_verified_attributes   = ["email"]
  mfa_configuration          = "OFF"
  deletion_protection        = "INACTIVE"
  email_verification_subject = "Verify your Companion Chat account"

  password_policy {
    minimum_length                   = 8
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = false
    require_uppercase                = true
    temporary_password_validity_days = 7
  }
}

resource "aws_cognito_user_pool_client" "app" {
  name                          = local.user_pool_client_name
  user_pool_id                  = aws_cognito_user_pool.this.id
  generate_secret               = false
  prevent_user_existence_errors = "ENABLED"
  supported_identity_providers  = ["COGNITO"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                 = var.allowed_oauth_flows
  allowed_oauth_scopes                = var.allowed_oauth_scopes

  explicit_auth_flows = [
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_USER_SRP_AUTH",
  ]

  callback_urls = var.callback_urls
  logout_urls   = var.logout_urls
}

resource "aws_cognito_user_pool_domain" "this" {
  domain       = lower(local.user_pool_domain_prefix)
  user_pool_id = aws_cognito_user_pool.this.id
}
