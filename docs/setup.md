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
