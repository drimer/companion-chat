# Development Guide

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

docs/                  # Documentation
├── setup.md          # Local development setup
├── api-usage.md      # API usage examples
├── testing.md        # Testing guide
├── deployment.md     # Deployment instructions
└── development.md    # This file - development guide

test-events/          # API testing scripts
├── README.md         # Testing documentation
├── api-gateway-examples.ps1  # Windows PowerShell script
└── api-gateway-examples.sh   # Bash script
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

## Code Style

- **Python**: Black formatting, type hints with mypy
- **Tests**: Comprehensive coverage across unit, integration, and e2e
- **Documentation**: Keep docs updated with code changes
- **Infrastructure**: Terraform for all AWS resources

## Technology Stack

- **Backend**: FastAPI with Python 3.11+
- **Database**: DynamoDB (local: Docker, production: AWS)
- **AI Integration**: OpenAI API via LangChain
- **Infrastructure**: AWS Lambda + API Gateway + DynamoDB
- **Testing**: pytest with multiple test levels
- **CI/CD**: GitHub Actions with Terraform
