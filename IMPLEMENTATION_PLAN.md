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

- [ ] **Modify `src/companionchat/db/repositories.py`**
  - [ ] Update `create()` method to store system prompt and user ID
  - [ ] Remove `store_new_message()` method
  - [ ] Update `get()` method to return new conversation structure
  - [ ] Add hardcoded system prompt constant: *"You are a language exchange student who speaks Japanese natively and wants to learn English. I am learning Japanese, and will help you improve your English as we speak."*
  - [ ] Add hardcoded user ID constant (temporary)

- [ ] **Update DynamoDB table structure**
  - [ ] Modify `infra/aws/modules/db/main.tf` if needed
  - [ ] Update local development setup in `README.md`

### 3. Add OpenAI Integration

- [ ] **Install dependencies**
  - [ ] Add `openai` to `pyproject.toml`
  - [ ] Add `langchain` and `langchain-openai` for state-of-the-art LLM integration
  - [ ] Add `pydantic-settings` for OpenAI API key management

- [ ] **Update settings in `src/companionchat/settings.py`**
  - [ ] Add `OPENAI_API_KEY: str` field
  - [ ] Add `OPENAI_MODEL: str` field with default "gpt-4o-mini"
  - [ ] Add `MAX_TOKENS: int` field with default 1000

- [ ] **Create OpenAI service**
  - [ ] Create `src/companionchat/services/` directory
  - [ ] Create `src/companionchat/services/__init__.py`
  - [ ] Create `src/companionchat/services/openai_service.py`
    - [ ] Implement `OpenAIService` class using langchain
    - [ ] Add method to process conversation with OpenAI
    - [ ] Add proper error handling and logging
    - [ ] Add token usage tracking

- [ ] **Update dependencies in `src/companionchat/dependencies.py`**
  - [ ] Add `OpenAIService` dependency
  - [ ] Create `get_openai_service()` function

### 4. Update API Endpoints

- [ ] **Modify `src/companionchat/main.py`**
  - [ ] Update `create_conversation` endpoint
    - [ ] Remove messages from response
    - [ ] Store system prompt and user ID
  - [ ] Update `get_conversation` endpoint
    - [ ] Return conversation metadata only (no messages)
  - [ ] Remove `store_new_message` endpoint
  - [ ] Remove `get_conversation_messages` endpoint
  - [ ] Add new `POST /conversations/{conversation_id}/chat` endpoint
    - [ ] Accept full conversation history from client
    - [ ] Send to OpenAI via service
    - [ ] Return AI response only

### 5. Environment Configuration

- [ ] **Update environment files**
  - [ ] Add OpenAI configuration to `.env.template`
  - [ ] Update AWS Lambda environment variables in `infra/aws/modules/conversations-lambda/main.tf`

### 6. Testing Implementation

- [ ] **Unit Tests**
  - [ ] Create `tests/` directory structure
  - [ ] Create `tests/unit/test_models.py`
    - [ ] Test updated `Conversation` model
    - [ ] Test new Pydantic schemas
  - [ ] Create `tests/unit/test_repositories.py`
    - [ ] Test `ConversationRepository.create()`
    - [ ] Test `ConversationRepository.get()`
    - [ ] Mock DynamoDB interactions
  - [ ] Create `tests/unit/test_openai_service.py`
    - [ ] Test OpenAI service with mocked responses
    - [ ] Test error handling scenarios
    - [ ] Test token limit handling

- [ ] **Integration Tests**
  - [ ] Create `tests/integration/test_api_endpoints.py`
    - [ ] Test conversation creation
    - [ ] Test conversation retrieval
    - [ ] Test chat endpoint with mocked OpenAI
  - [ ] Create `tests/integration/test_database.py`
    - [ ] Test with local DynamoDB container

- [ ] **End-to-End Tests**
  - [ ] Create `tests/e2e/test_full_conversation_flow.py`
    - [ ] Test complete user journey
    - [ ] Create conversation → chat → verify responses
    - [ ] Use real OpenAI API in staging environment

- [ ] **Test Configuration**
  - [ ] Update `pyproject.toml` with pytest configuration
  - [ ] Add test dependencies (pytest-asyncio, httpx, etc.)
  - [ ] Create `tests/conftest.py` with fixtures
  - [ ] Add test environment configuration

### 7. Documentation Updates

- [ ] **Update `README.md`**
  - [ ] Add OpenAI API key setup instructions
  - [ ] Update local development setup
  - [ ] Add example API usage
  - [ ] Update DynamoDB table creation command

- [ ] **API Documentation**
  - [ ] Update endpoint descriptions in FastAPI
  - [ ] Add comprehensive examples for chat endpoint
  - [ ] Document expected message format for conversation history

### 8. Deployment and Infrastructure

- [ ] **Update CI/CD**
  - [ ] Add OpenAI API key to GitHub secrets
  - [ ] Update `.github/workflows/deployment.yml` to run tests
  - [ ] Add environment-specific OpenAI configuration

- [ ] **Infrastructure Updates**
  - [ ] Add OpenAI API key to AWS Lambda environment variables
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

- **Started**: [Date]
- **Estimated Completion**: [Date]
- **Current Phase**: [Phase Number/Name]

---

*Last Updated: August 15, 2025*
