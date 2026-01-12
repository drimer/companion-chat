variable "group" {
  type        = string
  description = "Logical grouping for this identity component"
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev, stage, prod)"
}

variable "scope" {
  type        = string
  description = "Context label used in resource names"
}
