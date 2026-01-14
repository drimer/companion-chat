variable "group" {
    type = string
    description = "The logical grouping for this component in the system"
}

variable "environment" {
    type = string
    description = "The environment being deployed (ie. dev, stage, prod)"
}

variable "scope" {
    type = string
    description = "A free field to be coherent with the context of the component"
}

variable "lambda_function_name" {
    type = string
    description = "The name of the lambda function"
}

variable "lambda_function_handler" {
    type = string
    description = "The handler for the lambda function"
}

variable "lambda_function_runtime" {
    type = string
    description = "The runtime for the lambda function"
}

variable "db_conversations_table_arn" {
    type = string
    description = "The arn for the DynamoDB conversations table"
}

variable "db_conversations_table_name" {
    type = string
    description = "The name for the DynamoDB conversations table"
}

variable "db_users_table_arn" {
    type        = string
    description = "The ARN for the DynamoDB users table"
}

variable "db_users_table_name" {
    type        = string
    description = "The name for the DynamoDB users table"
}

variable "openai_model" {
    type = string
    description = "The OpenAI model to use for chat completion"
    default = "gpt-4o-mini"
}

variable "max_tokens" {
    type = string
    description = "Maximum tokens for OpenAI responses"
    default = "1000"
}

variable "deployment_package_key" {
    type = string
    description = "S3 key for the Lambda deployment package"
    default = "deployment.zip"
}

variable "openai_api_key" {
    type = string
    description = "The OpenAI API key for making API calls to OpenAI"
}