variable "aws_region" {
    description = "The AWS region to deploy the resources in"
    type = string
    default = "eu-west-2"
}

variable "openai_api_key" {
    description = "The OpenAI API key for making API calls to OpenAI"
    type = string
}

variable "cognito_callback_urls" {
    description = "Allowed OAuth callback URLs for the Cognito app client"
    type        = list(string)
    default     = []
}

variable "cognito_logout_urls" {
    description = "Allowed logout URLs for the Cognito app client"
    type        = list(string)
    default     = []
}