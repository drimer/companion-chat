# API Transformation Implementation Plan

This document outlines the complete plan to transform the companion-chat API from storing messages in conversations to a stateless conversation processor that integrates with OpenAI.

## Overview

The goal is to:
- Stop storing messages in conversations
- Store only conversation metadata (ID, system prompt, user ID)
- Implement OpenAI integration for chat responses
- Use client-side message storage
- Follow best practices with state-of-the-art libraries

## Implementation Checklist

### 1. Update Database Schema and Models

- [x] **Update `Conversation` model in `src/companionchat/db/models.py`**
  - [x] Remove `messages` field
  - [x] Add `system_prompt: str` field
  - [x] Add `user_id: str` field
  - [x] Add `created_at: datetime` field for better tracking

- [x] **Update Pydantic schemas in `src/companionchat/schemas/conversations.py`**
  - [x] Create `ConversationCreateRequest` schema
  - [x] Update `ConversationResponse` to include `system_prompt`, `user_id`, remove `messages`
  - [x] Create `ChatRequest` schema for incoming chat messages with full conversation history
  - [x] Create `ChatResponse` schema for OpenAI responses
  - [x] Create `MessageHistory` schema for client-side message storage

### 2. Update Repository Layer

- [x] **Modify `src/companionchat/db/repositories.py`**
  - [x] Update `create()` method to store system prompt and user ID
  - [x] Remove `store_new_message()` method
  - [x] Update `get()` method to return new conversation structure
  - [x] Add hardcoded system prompt constant: *"You are a language exchange student who speaks Japanese natively and wants to learn English. I am learning Japanese, and will help you improve your English as we speak."*
  - [x] Add hardcoded user ID constant (temporary)

- [ ] **Update DynamoDB table structure**
  - [ ] Modify `infra/aws/modules/db/main.tf` if needed
  - [ ] Update local development setup in `README.md`

### 3. Add OpenAI Integration

- [x] **Install dependencies**
  - [x] Add `openai` to `pyproject.toml`
  - [x] Add `langchain` and `langchain-openai` for state-of-the-art LLM integration
  - [x] Add `pydantic-settings` for OpenAI API key management

- [x] **Update settings in `src/companionchat/settings.py`**
  - [x] Add `OPENAI_API_KEY: str` field
  - [x] Add `OPENAI_MODEL: str` field with default "gpt-4o-mini"
  - [x] Add `MAX_TOKENS: int` field with default 1000

- [x] **Create OpenAI service**
  - [x] Create `src/companionchat/services/` directory
  - [x] Create `src/companionchat/services/__init__.py`
  - [x] Create `src/companionchat/services/openai_service.py`
    - [x] Implement `OpenAIService` class using langchain
    - [x] Add method to process conversation with OpenAI
    - [x] Add proper error handling and logging
    - [x] Add token usage tracking

- [x] **Update dependencies in `src/companionchat/dependencies.py`**
  - [x] Add `OpenAIService` dependency
  - [x] Create `get_openai_service()` function

### 4. Update API Endpoints

- [x] **Modify `src/companionchat/main.py`**
  - [x] Update `create_conversation` endpoint
    - [x] Remove messages from response
    - [x] Store system prompt and user ID
  - [x] Update `get_conversation` endpoint
    - [x] Return conversation metadata only (no messages)
  - [x] Remove `store_new_message` endpoint
  - [x] Remove `get_conversation_messages` endpoint
  - [x] Add new `POST /conversations/{conversation_id}/chat` endpoint
    - [x] Accept full conversation history from client
    - [x] Send to OpenAI via service
    - [x] Return AI response only

### 5. Environment Configuration

- [x] **Update environment files**
  - [x] Add OpenAI configuration to `.env.template`
  - [x] Update AWS Lambda environment variables in `infra/aws/modules/conversations-lambda/main.tf`

### 6. Testing Implementation

- [x] **Unit Tests**
  - [x] Create `tests/` directory structure
  - [x] Create `tests/unit/test_models.py`
    - [x] Test updated `Conversation` model
    - [x] Test new Pydantic schemas
  - [x] Create `tests/unit/test_repositories.py`
    - [x] Test `ConversationRepository.create()`
    - [x] Test `ConversationRepository.get()`
    - [x] Mock DynamoDB interactions
  - [x] Create `tests/unit/test_openai_service.py`
    - [x] Test OpenAI service with mocked responses
    - [x] Test error handling scenarios
    - [x] Test token limit handling

- [x] **Integration Tests**
  - [x] Create `tests/integration/test_api_endpoints.py`
    - [x] Test conversation creation
    - [x] Test conversation retrieval
    - [x] Test chat endpoint with mocked OpenAI
  - [x] Create `tests/integration/test_database.py`
    - [x] Test with local DynamoDB container

- [x] **End-to-End Tests**
  - [x] Create `tests/e2e/test_full_conversation_flow.py`
    - [x] Test complete user journey
    - [x] Create conversation → chat → verify responses
    - [x] Use real OpenAI API in staging environment

- [x] **Test Configuration**
  - [x] Update `pyproject.toml` with pytest configuration
  - [x] Add test dependencies (pytest-asyncio, httpx, etc.)
  - [x] Create `tests/conftest.py` with fixtures
  - [x] Add test environment configuration

### 7. Documentation Updates

- [x] **Update `README.md`**
  - [x] Add OpenAI API key setup instructions
  - [x] Update local development setup
  - [x] Add example API usage
  - [x] Update DynamoDB table creation command

- [x] **API Documentation**
  - [x] Update endpoint descriptions in FastAPI
  - [x] Add comprehensive examples for chat endpoint
  - [x] Document expected message format for conversation history

### 8. Deployment and Infrastructure

- [x] **Update CI/CD**
  - [x] Simplify OpenAI API key management (dummy value for initial deployment)
  - [x] Update Terraform configuration for manual API key update post-deployment
  - [x] Hardcode OpenAI model and token limits in dev environment

- [ ] **Infrastructure Updates**
  - [x] Add OpenAI environment variables to AWS Lambda (with dummy key)
  - [ ] Update IAM permissions if needed
  - [ ] Consider adding API Gateway rate limiting

### 9. Performance and Monitoring

- [ ] **Add Logging**
  - [ ] Implement structured logging for OpenAI interactions
  - [ ] Log conversation creation and chat requests
  - [ ] Add error tracking and monitoring

- [ ] **Add Validation**
  - [ ] Validate conversation history length
  - [ ] Implement rate limiting considerations
  - [ ] Add input sanitization for OpenAI requests

### 10. Security Considerations

- [ ] **API Security**
  - [ ] Add request validation for conversation ownership
  - [ ] Implement proper error handling to avoid information leakage
  - [ ] Add input sanitization and validation

- [ ] **OpenAI Integration Security**
  - [ ] Secure API key storage
  - [ ] Implement proper timeout handling
  - [ ] Add retry logic with exponential backoff

## Notes

- **System Prompt**: "You are a language exchange student who speaks Japanese natively and wants to learn English. I am learning Japanese, and will help you improve your English as we speak."
- **User ID**: Will be hardcoded temporarily until authentication is implemented
- **OpenAI Model**: Using gpt-4o-mini as the default model
- **Architecture**: Client stores conversation history, API processes requests statefully with OpenAI

## Progress Tracking

- **Started**: August 15, 2025
- **Estimated Completion**: August 16, 2025
- **Current Phase**: Implementation Complete - Ready for Deployment
- **Completed**: Database models, API endpoints, OpenAI integration, unit tests, integration tests, E2E tests, environment configuration, documentation updates
- **Next**: Deployment, CI/CD updates, monitoring

---

*Last Updated: August 15, 2025*
