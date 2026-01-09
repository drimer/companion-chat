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

## Authentication & SSO

- API Gateway enforces Cognito SSO with the `CompanionChatAuthorizer`. Every request must send an `Authorization: Bearer <access_token>` header so FastAPI can read the caller's `sub` via `get_authenticated_sub()`.
- Local development can still send any opaque bearer token (for example `Authorization: Bearer local-user-123`) because the dependency override treats the provided token as the acting Cognito `sub`.
- Cognito resources (user pool + app client) are deployed through Terraform to keep infrastructure and application releases coupled inside the same pipeline.

## DynamoDB Schema Updates

- `conversations` table now includes a `user_id` attribute with a `user_id-index` GSI so repositories can efficiently list and authorize records per owner.
- A dedicated `users` table (partition key `sub`) stores Cognito profile metadata via the `UserRepository.upsert_from_claims()` helper.
- The Lambda receives both `DB_CONVERSATIONS_TABLE_NAME` and `DB_USERS_TABLE_NAME` so ownership checks and profile caching stay isolated from request handling code.
