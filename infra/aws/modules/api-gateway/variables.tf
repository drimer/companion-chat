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

variable "lambda_function_arn" {
    type = string
    description = "ARN of the Lambda function to integrate with"
}

variable "lambda_function_name" {
    type = string
    description = "Name of the Lambda function to integrate with"
}

variable "cognito_user_pool_arn" {
    type        = string
    description = "ARN of the Cognito user pool used by the CompanionChatAuthorizer"
}
