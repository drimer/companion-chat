locals {
    conversations_table_name = join("-", compact(tolist([var.group, var.environment, var.scope, var.table_name, "db"])))
    users_table_name         = join("-", compact(tolist([var.group, var.environment, var.scope, var.users_table_name, "db"])))
}

resource "aws_dynamodb_table" "conversations_table" {
    name         = local.conversations_table_name
    billing_mode = var.billing_mode
    hash_key     = "id"

    attribute {
      name = "id"
      type = "S"
    }

    attribute {
      name = "user_id"
      type = "S"
    }

    global_secondary_index {
      name            = "user_id-index"
      hash_key        = "user_id"
      projection_type = "ALL"
    }
}

resource "aws_dynamodb_table" "users_table" {
    name         = local.users_table_name
    billing_mode = var.billing_mode
    hash_key     = "sub"

    attribute {
      name = "sub"
      type = "S"
    }
}