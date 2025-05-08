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

resource "aws_iam_role" "api_lambda_role" {
  name               = "api_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_lambda_function" "test_lambda" {
  function_name = join("-", compact(tolist([var.group, var.environment, var.scope, var.lambda_function_name])))
  role          = aws_iam_role.api_lambda_role.arn
  handler       = "com.companion.companionchat.LambdaHandler::handleRequest"
  filename = "${path.module}/../../../../build/distributions/companion-chat-0.0.1-SNAPSHOT.zip"
  source_code_hash = filebase64sha256("${path.module}/../../../../build/distributions/companion-chat-0.0.1-SNAPSHOT.zip")
  runtime = var.lambda_function_runtime
  memory_size = 128
  timeout = 30

  environment {
    variables = {
      foo = "bar"
    }
  }
}