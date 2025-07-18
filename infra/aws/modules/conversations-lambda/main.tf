data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "conversations_lambda_role" {
  name               = "conversations_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_policy" "conversations_lambda_policy" {
  name = "conversations_lambda_policy"
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem"
        ],
        "Resource": [
          "${var.dynamodb_conversations_table_arn}"
        ]
      }
    ]
  })  
}

resource "aws_lambda_function" "test_lambda" {
  function_name = join("-", compact(tolist([var.group, var.environment, var.scope, var.lambda_function_name])))
  role          = aws_iam_role.conversations_lambda_role.arn
  handler       = var.lambda_function_handler
  filename = "${path.module}/../../../../deployment.zip"
  source_code_hash = filebase64sha256("${path.module}/../../../../deployment.zip")
  runtime = var.lambda_function_runtime
  memory_size = 128
  timeout = 30
}

resource "aws_iam_role_policy_attachment" "conversations_lambda_policy_attachment" {
  role = aws_iam_role.conversations_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}