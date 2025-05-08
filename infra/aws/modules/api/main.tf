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

data "archive_file" "api_lambda_archive_file" {
  type        = "zip"
  source_file = "${path.module}/../../../../build/libs/companion-chat-0.0.1-SNAPSHOT.jar"
  output_path = "api_lambda_function_payload.zip"
}

resource "aws_lambda_function" "test_lambda" {
#   filename      = "api_lambda_function_payload.zip"
  filename = data.archive_file.api_lambda_archive_file.output_path
  function_name = join("-", compact(tolist([var.group, var.environment, var.scope, var.lambda_function_name])))
  role          = aws_iam_role.api_lambda_role.arn
  handler       = "com.companion.companionchat.LambdaHandler::handleRequest"

  source_code_hash = data.archive_file.api_lambda_archive_file.output_base64sha256

  runtime = var.lambda_function_runtime
  memory_size = 128
  timeout = 30

  environment {
    variables = {
      foo = "bar"
    }
  }
}