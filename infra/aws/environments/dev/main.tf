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
}

module "db" {
    source = "../../modules/db"
    table_name = "conversations"
    group = local.group_global
    environment = local.environment
    scope = "chat"
    billing_mode = "PAY_PER_REQUEST"
}

module "conversations_lambda" {
    source = "../../modules/conversations-lambda"
    group = local.group_global
    environment = local.environment
    scope = "chat"
    lambda_function_name = "conversations-lambda"
    lambda_function_handler = "src.companionchat.main.handler"
    lambda_function_runtime = "python3.10"
    dynamodb_conversations_table_arn = module.db.conversations_table_arn
}
