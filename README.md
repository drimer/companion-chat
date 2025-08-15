# companion-chat

Companion Chat app - AI-powered conversation assistant with Japanese language exchange capabilities.

## Quick Start

### Local Development
```bash
# 1. Set up environment
cp .env.template .env  # Add your OpenAI API key
poetry install

# 2. Start local infrastructure
docker-compose -f ./infra/docker-compose.yml up -d

# 3. Create DynamoDB table
aws dynamodb create-table \
  --table-name conversations \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
  --endpoint-url http://localhost:8000

# 4. Start the server
poetry run uvicorn src.companionchat.main:app --reload --port 4000
```

### Testing the Production API
```bash
# Windows
powershell.exe -File "test-events/api-gateway-examples.ps1"

# Linux/macOS/WSL
bash test-events/api-gateway-examples.sh
```

## Documentation

| Document | Description |
|----------|-------------|
| **[Setup Guide](docs/setup.md)** | Complete local development setup |
| **[API Usage](docs/api-usage.md)** | API endpoints and examples |
| **[Testing](docs/testing.md)** | Running tests and API validation |
| **[Deployment](docs/deployment.md)** | AWS deployment instructions |
| **[Development](docs/development.md)** | Project structure and contributing |

## Features

- 🤖 **AI-Powered Chat**: OpenAI integration for intelligent conversations
- 🇯🇵 **Japanese Language Exchange**: Native Japanese conversation practice
- 🚀 **Serverless**: AWS Lambda + API Gateway deployment
- 📊 **Token Tracking**: Monitor OpenAI API usage
- 🔄 **Cross-Platform Testing**: PowerShell and Bash testing scripts
- 🐳 **Local Development**: Docker-based local DynamoDB

## Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **AI**: OpenAI API via LangChain
- **Database**: DynamoDB
- **Infrastructure**: AWS Lambda, API Gateway, S3
- **Testing**: pytest, cross-platform API scripts
- **CI/CD**: GitHub Actions, Terraform

## API Endpoints

- `POST /conversations` - Create new conversation
- `POST /conversations/{id}/chat` - Send chat message
- `GET /conversations/{id}` - Get conversation details
- `GET /health` - Health check

## License

See [LICENSE](LICENSE) file for details.