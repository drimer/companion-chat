# Testing Guide

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

## API Testing

For comprehensive API testing documentation, see the [test-events/README.md](../test-events/README.md) file.

### Quick API Tests

**Local Development:**
```bash
# Test local API
curl http://localhost:4000/health
```

**Production (AWS):**
```bash
# Test deployed API Gateway
powershell.exe -File "test-events/api-gateway-examples.ps1"  # Windows
bash test-events/api-gateway-examples.sh                    # Linux/macOS
```
