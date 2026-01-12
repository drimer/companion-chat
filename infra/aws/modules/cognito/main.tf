locals {
  user_pool_name          = join("-", compact(tolist([var.group, var.environment, var.scope, "users"])))
  user_pool_client_name   = "${local.user_pool_name}-client"
  user_pool_domain_prefix = var.domain_prefix != "" ? var.domain_prefix : replace(local.user_pool_name, "_", "-")
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

locals {
  user_pool_domain_hash = substr(sha1("${data.aws_caller_identity.current.account_id}-${local.user_pool_domain_prefix}"), 0, 6)
  user_pool_domain_name = lower("${local.user_pool_domain_prefix}-${local.user_pool_domain_hash}")
}

resource "aws_cognito_user_pool" "this" {
  name                       = local.user_pool_name
  auto_verified_attributes   = ["email"]
  username_attributes        = ["email"]
  mfa_configuration          = "OFF"
  deletion_protection        = "INACTIVE"

  password_policy {
    minimum_length                   = 8
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = false
    require_uppercase                = true
    temporary_password_validity_days = 7
    password_history_size = 0
  }

  account_recovery_setting {
    recovery_mechanism {
      name = "verified_email"
      priority = 1
    }
    recovery_mechanism {
      name = "verified_phone_number"
      priority = 2
    }
  }

  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  sign_in_policy {
    allowed_first_auth_factors = ["PASSWORD"] 
  }

  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_subject = "Verify your Companion Chat account"
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
    "ALLOW_USER_AUTH",
    "ALLOW_USER_SRP_AUTH",
  ]

  callback_urls = var.callback_urls
  logout_urls   = var.logout_urls

  access_token_validity = 60
  id_token_validity     = 60
  refresh_token_validity = 30

  token_validity_units {
    access_token = "minutes"
    id_token = "minutes"
    refresh_token = "days"
  }
}

resource "aws_cognito_user_pool_domain" "managed" {
  domain                 = local.user_pool_domain_name
  user_pool_id           = aws_cognito_user_pool.this.id
  managed_login_version  = 2
}
