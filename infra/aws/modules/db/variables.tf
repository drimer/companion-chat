variable "table_name" {
    type = string
    description = "The name for the DynamoDB table"
}

variable "billing_mode" {
    type = string
    default = "PAY_PER_REQUEST"
}

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
