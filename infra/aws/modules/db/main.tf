locals {
    table_name = join("-", compact(tolist([var.group, var.environment, var.scope, var.table_name, "db"])))
}

resource "aws_dynamodb_table" "conversations_table" {
    name = local.table_name
    billing_mode = var.billing_mode
    hash_key = "id"

    attribute {
      name = "id"
      type = "S"
    }
}