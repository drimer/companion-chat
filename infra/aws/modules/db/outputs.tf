output "dynamodb_table_name" {
    value = aws_dynamodb_table.conversations_table.name
}

output "dynamodb_table_arn" {
    value = aws_dynamodb_table.conversations_table.arn
}

output "conversations_table_arn" {
    value = aws_dynamodb_table.conversations_table.arn

}