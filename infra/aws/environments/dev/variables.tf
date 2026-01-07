variable "aws_region" {
    description = "The AWS region to deploy the resources in"
    type = string
    default = "eu-west-2"
}

variable "openai_api_key" {
    description = "The OpenAI API key for making API calls to OpenAI"
    type = string
}