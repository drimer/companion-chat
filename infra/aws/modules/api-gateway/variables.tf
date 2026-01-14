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

variable "log_retention_in_days" {
    type        = number
    description = "CloudWatch Logs retention for API Gateway access logs"
    default     = 14
}

variable "execution_log_level" {
    type        = string
    description = "Execution logging level for API Gateway stage"
    default     = "INFO"
}

variable "enable_execution_logs" {
    type        = bool
    description = "Whether to enable detailed execution logs (data trace)"
    default     = true
}
