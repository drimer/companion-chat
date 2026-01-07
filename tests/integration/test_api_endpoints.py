"""
Integration tests for API endpoints.
These tests run against the actual FastAPI application with mocked external dependencies.
"""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from companionchat.dependencies import (
    get_authenticated_sub,
    get_conversation_authorization_service,
    get_conversation_repository,
    get_openai_service,
)
from companionchat.main import app
from companionchat.schemas.conversations import ChatResponse, MessageResponse

AUTH_SUB = "test-sub-001"


@pytest.fixture
def mock_conversation_repository():
    """Mock the conversation repository."""
    return AsyncMock()


@pytest.fixture
def mock_conversation_authorizer():
    """Mock the conversation authorization service."""
    authorizer = MagicMock()
    authorizer.ensure_owner = MagicMock()
    return authorizer


@pytest.fixture
def mock_openai_service():
    """Mock the OpenAI service."""
    return AsyncMock()


@pytest.fixture
async def async_client(
    mock_conversation_repository,
    mock_openai_service,
    mock_conversation_authorizer,
):
    """Create an async HTTP client for testing with mocked dependencies."""
    # Override dependencies
    app.dependency_overrides[get_conversation_repository] = (
        lambda: mock_conversation_repository
    )
    app.dependency_overrides[get_openai_service] = lambda: mock_openai_service
    app.dependency_overrides[get_authenticated_sub] = lambda: AUTH_SUB
    app.dependency_overrides[get_conversation_authorization_service] = (
        lambda: mock_conversation_authorizer
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    # Clean up dependency overrides
    app.dependency_overrides.clear()


class TestConversationEndpoints:
    """Test conversation CRUD endpoints."""

    async def test_create_conversation(
        self, async_client, mock_conversation_repository, mock_openai_service
    ):
        """Test conversation creation endpoint."""
        # Arrange
        conversation_id = str(uuid.uuid4())
        mock_conversation = MagicMock()
        mock_conversation.id = conversation_id
        mock_conversation.system_prompt = "You are a language exchange student who speaks Japanese natively and wants to learn English. I am learning Japanese, and will help you improve your English as we speak."
        mock_conversation.user_id = AUTH_SUB
        mock_conversation.created_at = datetime.now()

        mock_conversation_repository.create.return_value = mock_conversation
        mock_openai_service.generate_initial_message.return_value = MessageResponse(
            role="assistant",
            content="こんにちは！今日は素敵なレストランでお会いしましょう。",
        )

        # Act
        response = await async_client.post("/conversations")

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == conversation_id  # Should match mock
        assert data["system_prompt"] == mock_conversation.system_prompt
        assert data["user_id"] == mock_conversation.user_id
        assert "created_at" in data
        assert data["messages"] == [
            {
                "role": "assistant",
                "content": "こんにちは！今日は素敵なレストランでお会いしましょう。",
            }
        ]

        mock_conversation_repository.create.assert_awaited_once_with(AUTH_SUB)
        mock_openai_service.generate_initial_message.assert_awaited_once_with(
            mock_conversation.system_prompt
        )

    async def test_get_conversation(
        self,
        async_client,
        mock_conversation_repository,
        mock_conversation_authorizer,
    ):
        """Test conversation retrieval endpoint."""
        # Arrange
        conversation_id = str(uuid.uuid4())
        mock_conversation = MagicMock()
        mock_conversation.id = conversation_id
        mock_conversation.system_prompt = "You are a language exchange student who speaks Japanese natively and wants to learn English. I am learning Japanese, and will help you improve your English as we speak."
        mock_conversation.user_id = AUTH_SUB
        mock_conversation.created_at = datetime.now()

        mock_conversation_repository.get.return_value = mock_conversation

        # Act
        response = await async_client.get(f"/conversations/{conversation_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == conversation_id
        assert "system_prompt" in data
        assert "user_id" in data
        assert "created_at" in data
        assert data["messages"] == []

        mock_conversation_repository.get.assert_awaited_once_with(conversation_id)
        mock_conversation_authorizer.ensure_owner.assert_called_once_with(
            mock_conversation, AUTH_SUB
        )

    async def test_get_nonexistent_conversation(
        self, async_client, mock_conversation_repository
    ):
        """Test retrieving a conversation that doesn't exist."""
        # Arrange
        conversation_id = str(uuid.uuid4())
        mock_conversation_repository.get.return_value = None

        # Act
        response = await async_client.get(f"/conversations/{conversation_id}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Conversation not found"

    async def test_get_conversation_forbidden(
        self,
        async_client,
        mock_conversation_repository,
        mock_conversation_authorizer,
    ):
        conversation_id = str(uuid.uuid4())
        mock_conversation = MagicMock()
        mock_conversation.id = conversation_id
        mock_conversation.system_prompt = "Prompt"
        mock_conversation.user_id = "other-user"
        mock_conversation.created_at = datetime.now()

        mock_conversation_repository.get.return_value = mock_conversation
        mock_conversation_authorizer.ensure_owner.side_effect = PermissionError()

        response = await async_client.get(f"/conversations/{conversation_id}")

        assert response.status_code == 403
        assert response.json()["detail"] == "Forbidden"


class TestChatEndpoint:
    """Test the chat endpoint with OpenAI integration."""

    async def test_chat_with_conversation(
        self,
        async_client,
        mock_conversation_repository,
        mock_openai_service,
        mock_conversation_authorizer,
    ):
        """Test chat endpoint with mocked OpenAI service."""
        # Arrange
        conversation_id = str(uuid.uuid4())

        # Mock conversation exists
        mock_conversation = MagicMock()
        mock_conversation.id = conversation_id
        mock_conversation.system_prompt = "You are a language exchange student who speaks Japanese natively and wants to learn English. I am learning Japanese, and will help you improve your English as we speak."
        mock_conversation.user_id = AUTH_SUB
        mock_conversation_repository.get.return_value = mock_conversation

        # Mock OpenAI response
        mock_chat_response = ChatResponse(
            message="Hello! I'm excited to practice English with you. どうぞよろしくお願いします！",
            usage={"prompt_tokens": 25, "completion_tokens": 20, "total_tokens": 45},
        )
        mock_openai_service.process_chat_request.return_value = mock_chat_response

        # Prepare request data
        chat_request = {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! I'm ready to practice Japanese with you.",
                }
            ]
        }

        # Act
        response = await async_client.post(
            f"/conversations/{conversation_id}/chat", json=chat_request
        )

        # Debug: Print response content if not 200
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert (
            data["message"]
            == "Hello! I'm excited to practice English with you. どうぞよろしくお願いします！"
        )
        assert "usage" in data
        assert data["usage"]["total_tokens"] == 45

        # Verify service calls
        mock_conversation_repository.get.assert_awaited_once_with(conversation_id)
        mock_conversation_authorizer.ensure_owner.assert_called_once_with(
            mock_conversation, AUTH_SUB
        )
        mock_openai_service.process_chat_request.assert_awaited_once()

    async def test_chat_with_nonexistent_conversation(
        self,
        async_client,
        mock_conversation_repository,
        mock_openai_service,
    ):
        """Test chat endpoint with conversation that doesn't exist."""
        # Arrange
        conversation_id = str(uuid.uuid4())
        mock_conversation_repository.get.side_effect = ValueError(
            f"Conversation with ID {conversation_id} not found."
        )

        chat_request = {"messages": [{"role": "user", "content": "Hello!"}]}

        # Act
        response = await async_client.post(
            f"/conversations/{conversation_id}/chat", json=chat_request
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

        # Verify OpenAI service was not called
        mock_openai_service.process_chat_request.assert_not_called()

    async def test_chat_forbidden_for_other_user(
        self,
        async_client,
        mock_conversation_repository,
        mock_openai_service,
        mock_conversation_authorizer,
    ):
        conversation_id = str(uuid.uuid4())
        mock_conversation = MagicMock()
        mock_conversation.id = conversation_id
        mock_conversation.system_prompt = "Prompt"
        mock_conversation.user_id = "different"
        mock_conversation_repository.get.return_value = mock_conversation
        mock_conversation_authorizer.ensure_owner.side_effect = PermissionError()

        chat_request = {
            "messages": [
                {"role": "user", "content": "Hello!"},
            ]
        }

        response = await async_client.post(
            f"/conversations/{conversation_id}/chat", json=chat_request
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Forbidden"
        mock_openai_service.process_chat_request.assert_not_called()

    async def test_chat_with_empty_conversation_history(
        self,
        async_client,
        mock_conversation_repository,
        mock_openai_service,
        mock_conversation_authorizer,
    ):
        """Test chat endpoint with empty conversation history."""
        # Arrange
        conversation_id = str(uuid.uuid4())

        mock_conversation = MagicMock()
        mock_conversation.id = conversation_id
        mock_conversation.system_prompt = "Test prompt"
        mock_conversation.user_id = AUTH_SUB
        mock_conversation_repository.get.return_value = mock_conversation

        # Mock OpenAI response for empty messages
        mock_chat_response = ChatResponse(
            message="I'm ready to chat! Please send me a message.",
            usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25},
        )
        mock_openai_service.process_chat_request.return_value = mock_chat_response

        chat_request = {"messages": []}

        # Act
        response = await async_client.post(
            f"/conversations/{conversation_id}/chat", json=chat_request
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "usage" in data
        mock_conversation_authorizer.ensure_owner.assert_called_once_with(
            mock_conversation, AUTH_SUB
        )

    async def test_chat_with_invalid_message_format(
        self, async_client, mock_conversation_repository
    ):
        """Test chat endpoint with invalid message format."""
        # Arrange
        conversation_id = str(uuid.uuid4())

        mock_conversation = MagicMock()
        mock_conversation.id = conversation_id
        mock_conversation.user_id = AUTH_SUB
        mock_conversation_repository.get.return_value = mock_conversation

        # Missing 'role' field
        chat_request = {"messages": [{"content": "Hello!"}]}

        # Act
        response = await async_client.post(
            f"/conversations/{conversation_id}/chat", json=chat_request
        )

        # Assert
        assert response.status_code == 422  # Validation error


class TestHealthEndpoint:
    """Test health check endpoint."""

    async def test_health_check(self, async_client):
        """Test health check endpoint."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
