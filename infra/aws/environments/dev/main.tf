terraform {
    required_version = "~> 1.11"
    required_providers {
        aws = {
            source = "hashicorp/aws"
        }
    }

    backend "s3" {
        bucket = "companion-chat-terraform-state"
        key = "org/orgState/dev-companionchat"
        region = "eu-west-2"
        # assume_role = {
        #     role_arn = "<fill in>"
        # }
    }
}

provider "aws" {
    region = var.aws_region
    default_tags {
        tags = {
            ManagedBy = "Terraform"
            Repository = "companion-chat"
            Environment = local.environment
        }
    }
}

locals {
    environment = terraform.workspace == "default" ? "dev" : terraform.workspace
    group_global = "companion-chat"
    cognito_domain_prefix = var.cognito_domain_prefix != "" ? var.cognito_domain_prefix : join("-", compact(tolist([local.group_global, local.environment, "chat", "auth"])))
}

module "db" {
    source = "../../modules/db"
    table_name = "conversations"
    users_table_name = "users"
    group = local.group_global
    environment = local.environment
    scope = "chat"
    billing_mode = "PAY_PER_REQUEST"
}

module "cognito" {
    source      = "../../modules/cognito"
    group       = local.group_global
    environment = local.environment
    scope       = "chat"
    callback_urls = var.cognito_callback_urls
    logout_urls   = var.cognito_logout_urls
    domain_prefix = lower(local.cognito_domain_prefix)
}

module "conversations_lambda" {
    source = "../../modules/conversations-lambda"
    group = local.group_global
    environment = local.environment
    scope = "chat"
    lambda_function_name = "conversations-lambda"
    lambda_function_handler = "src.companionchat.main.handler"
    lambda_function_runtime = "python3.10"
    db_conversations_table_arn = module.db.conversations_table_arn
    db_conversations_table_name = module.db.conversations_table_name
    db_users_table_arn = module.db.users_table_arn
    db_users_table_name = module.db.users_table_name
    openai_model = "gpt-4o-mini"
    max_tokens = "1000"
    openai_api_key = var.openai_api_key
}

module "api_gateway" {
    source = "../../modules/api-gateway"
    group = local.group_global
    environment = local.environment
    scope = "chat"
    lambda_function_arn = module.conversations_lambda.lambda_function_arn
    lambda_function_name = module.conversations_lambda.lambda_function_name
    cognito_user_pool_arn = module.cognito.user_pool_arn
}
