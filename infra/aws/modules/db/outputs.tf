output "dynamodb_table_name" {
    value = aws_dynamodb_table.chats_table.name
}

output "dynamodb_table_arn" {
    value = aws_dynamodb_table.chats_table.arn
}

output "conversations_table_arn" {
    value = aws_dynamodb_table.chats_table.arn

}