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

variable "callback_urls" {
  type        = list(string)
  description = "Allowed OAuth callback URLs"
  default     = ["companionchat://auth/callback"]
}

variable "logout_urls" {
  type        = list(string)
  description = "Allowed logout URLs"
  default     = ["companionchat://auth/callback"]
}

variable "domain_prefix" {
  type        = string
  description = "Domain prefix for the Cognito hosted UI"
  default     = ""
}

variable "allowed_oauth_flows" {
  type        = list(string)
  description = "OAuth grant types enabled on the hosted UI"
  default     = ["code"]
}

variable "allowed_oauth_scopes" {
  type        = list(string)
  description = "OAuth scopes granted to hosted UI clients"
  default     = ["email", "openid", "profile", "oauth2"]
}
