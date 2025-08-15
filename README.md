# companion-chat

Companion Chat app - for all your needs.


# Setup for Local Development

## Prerequisites

1. **Docker & docker-compose**: https://docs.docker.com/compose/install/
2. **AWS CLI**: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
3. **Poetry**: https://python-poetry.org/docs/#installation
4. **OpenAI API Key**: Sign up at https://platform.openai.com/

## Environment Setup

1. **Clone and navigate to the project**:
```bash
git clone <repository-url>
cd companion-chat
```

2. **Set up environment variables**:
```bash
cp .env.template .env

# Edit .env with your values:
# OPENAI_API_KEY=your_actual_openai_api_key_here
# OPENAI_MODEL=gpt-4o-mini  # or your preferred model
# MAX_TOKENS=1000
```

3. **Install Python dependencies**:
```bash
poetry install
```

## Local Infrastructure

1. **Start local DynamoDB**:
```bash
docker-compose -f ./infra/docker-compose.yml up -d
```

2. **Create the conversations table**:
```bash
aws dynamodb create-table \
  --table-name conversations \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
  --table-class STANDARD \
  --endpoint-url http://localhost:8000
```

## Running the Application

**Start the development server**:
```bash
poetry run uvicorn src.companionchat.main:app --reload --port 4000
```

The API will be available at:
- **API**: http://localhost:4000
- **Documentation**: http://localhost:4000/docs
- **Health Check**: http://localhost:4000/health

# API Usage

## Create a Conversation

```bash
curl -X POST "http://localhost:4000/conversations" \
  -H "Content-Type: application/json"
```

**Response**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "system_prompt": "You are a language exchange student who speaks Japanese natively and wants to learn English. I am learning Japanese, and will help you improve your English as we speak.",
  "user_id": "test-user-001",
  "created_at": "2025-08-15T10:30:00Z"
}
```

## Chat with OpenAI

```bash
curl -X POST "http://localhost:4000/conversations/{conversation_id}/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hello! I want to practice Japanese with you."
      }
    ]
  }'
```

**Response**:
```json
{
  "message": "Hello! こんにちは！I'm excited to practice English with you while helping you learn Japanese. 一緒に頑張りましょう！How should we start?",
  "usage": {
    "prompt_tokens": 45,
    "completion_tokens": 32,
    "total_tokens": 77
  }
}
```

## Get Conversation Metadata

```bash
curl "http://localhost:4000/conversations/{conversation_id}"
```

# Testing

## Unit Tests
```bash
# Run all unit tests
poetry run pytest tests/unit/ -v

# Run specific test file
poetry run pytest tests/unit/test_openai_service.py -v
```

## Integration Tests
```bash
# Run integration tests (requires local DynamoDB)
poetry run pytest tests/integration/ -v

# Skip database tests if needed
SKIP_DB_TESTS=true poetry run pytest tests/integration/ -v
```

## End-to-End Tests
```bash
# Run E2E tests (requires real OpenAI API key)
poetry run pytest tests/e2e/ -v -m e2e

# Skip performance tests
SKIP_PERFORMANCE_TESTS=true poetry run pytest tests/e2e/ -v -m e2e
```

## All Tests
```bash
poetry run pytest -v
```


# Deployment

## Manual Steps required for a brand new deployment in AWS

1. **Create S3 bucket for Terraform state**:
   ```bash
   aws s3 mb s3://companion-chat-terraform-state
   ```

2. **Create IAM user for Terraform** with the following policy:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "VisualEditor0",
         "Effect": "Allow",
         "Action": [
           "s3:*",
           "dynamodb:*",
           "lambda:*",
           "iam:*",
           "logs:*",
		   "apigateway:*"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

3. **Deploy to AWS using GitHub Actions**

4. **Update OpenAI API Key after deployment**:
   The Lambda function is deployed with a dummy OpenAI API key. You need to update it manually via AWS Console:
   
   - Go to AWS Lambda Console
   - Find the `conversations-lambda` function (name will be like: `companion-chat-dev-chat-conversations-lambda`)
   - Go to Configuration → Environment variables
   - Update `OPENAI_API_KEY` with your real API key
   - Click "Save"

## Automated Deployment

Deployments are automated with GitHub Actions. The pipeline:
1. Runs all tests (unit, integration, e2e)
2. Builds deployment package
3. Deploys to AWS using Terraform

### Terraform Validation Commands

For validation and troubleshooting purposes only. **Actual deployment should always be done via GitHub Actions.**

```bash
# Validate deployment configuration
terraform -chdir=infra/aws/environments/dev plan

# Initialize if needed
terraform -chdir=infra/aws/environments/dev init
```

# Development

## Project Structure

```
src/companionchat/
├── main.py              # FastAPI application and routes
├── settings.py          # Configuration management
├── dependencies.py      # Dependency injection setup
├── db/
│   ├── models.py        # Data models
│   └── repositories.py  # Database operations
├── schemas/
│   └── conversations.py # Pydantic schemas for validation
└── services/
    └── openai_service.py # OpenAI integration via Langchain

tests/
├── unit/               # Unit tests with mocks
├── integration/        # Integration tests with real DB
└── e2e/               # End-to-end tests with real OpenAI

infra/
├── aws/               # Terraform infrastructure
└── docker/            # Local development setup
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run the full test suite
5. Submit a pull request

```bash
# Before submitting PR, run:
poetry run pytest -v                    # All tests
poetry run black src/ tests/           # Code formatting
poetry run mypy src/                   # Type checking
```