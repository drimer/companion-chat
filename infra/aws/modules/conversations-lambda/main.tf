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
          "${var.db_conversations_table_arn}"
        ]
      },
      {
        "Effect": "Allow",
        "Action": [
          "s3:GetObject"
        ],
        "Resource": [
          "${aws_s3_bucket.lambda_deployments.arn}/*"
        ]
      }
    ]
  })  
}

# S3 bucket for storing Lambda deployment packages
resource "aws_s3_bucket" "lambda_deployments" {
  bucket = "${var.group}-${var.environment}-lambda-deployments"
}

resource "aws_s3_bucket_versioning" "lambda_deployments_versioning" {
  bucket = aws_s3_bucket.lambda_deployments.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Upload deployment package to S3
resource "aws_s3_object" "lambda_deployment_package" {
  bucket = aws_s3_bucket.lambda_deployments.bucket
  key    = "deployment.zip"
  source = "${path.module}/../../../../deployment.zip"
  source_hash = filemd5("${path.module}/../../../../deployment.zip")
}

resource "aws_lambda_function" "conversations" {
  function_name = join("-", compact(tolist([var.group, var.environment, var.scope, var.lambda_function_name])))
  role          = aws_iam_role.conversations_lambda_role.arn
  handler       = var.lambda_function_handler
  
  # Use S3 instead of direct file upload
  s3_bucket     = aws_s3_bucket.lambda_deployments.bucket
  s3_key        = aws_s3_object.lambda_deployment_package.key
  source_code_hash = "${filemd5("${path.module}/../../../../deployment.zip")}"
  
  runtime = var.lambda_function_runtime
  memory_size = 128
  timeout = 30
  environment {
    variables = {
      DB_CONVERSATIONS_TABLE_NAME = var.db_conversations_table_name
      OPENAI_API_KEY = var.openai_api_key
      OPENAI_MODEL = var.openai_model
      MAX_TOKENS = var.max_tokens
    }
  }
}

resource "aws_iam_role_policy_attachment" "conversations_lambda_policy_attachment" {
  role = aws_iam_role.conversations_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "conversations_lambda_policy_attachment_2" {
  role = aws_iam_role.conversations_lambda_role.name
  policy_arn = aws_iam_policy.conversations_lambda_policy.arn
}