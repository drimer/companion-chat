from unittest.mock import AsyncMock, MagicMock

import pytest

from src.companionchat.schemas.conversations import ChatRequest, MessageHistory
from src.companionchat.services.openai_service import OpenAIService


@pytest.fixture
def mock_client():
    """Create a mock ChatOpenAI client."""
    return AsyncMock()


@pytest.fixture
def openai_service(mock_client):
    """Create OpenAIService with mocked client."""
    return OpenAIService(mock_client)


def test_convert_messages_to_langchain(openai_service):
    """Test message conversion to Langchain format."""
    system_prompt = "Test system prompt"
    messages = [
        MessageHistory(role="user", content="Hello"),
        MessageHistory(role="assistant", content="Hi there!"),
        MessageHistory(role="user", content="How are you?"),
    ]

    langchain_messages = openai_service._convert_messages_to_langchain(
        system_prompt, messages
    )

    assert len(langchain_messages) == 4  # 1 system + 3 messages
    assert langchain_messages[0].content == system_prompt
    assert langchain_messages[1].content == "Hello"
    assert langchain_messages[2].content == "Hi there!"
    assert langchain_messages[3].content == "How are you?"


@pytest.mark.asyncio
async def test_process_chat_request_success(openai_service, mock_client):
    """Test successful chat request processing."""
    mock_response = MagicMock()
    mock_response.content = "I'm doing well, thank you!"
    mock_response.response_metadata = {
        "token_usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18}
    }
    mock_client.ainvoke.return_value = mock_response

    system_prompt = "Test system prompt"
    chat_request = ChatRequest(
        messages=[MessageHistory(role="user", content="How are you?")]
    )

    response = await openai_service.process_chat_request(system_prompt, chat_request)

    assert response.message == "I'm doing well, thank you!"
    assert response.usage["prompt_tokens"] == 10
    assert response.usage["completion_tokens"] == 8
    assert response.usage["total_tokens"] == 18
    mock_client.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_process_chat_request_no_usage_metadata(openai_service, mock_client):
    """Test chat request processing with no usage metadata."""
    mock_response = MagicMock()
    mock_response.content = "Hello!"
    mock_response.response_metadata = None
    mock_client.ainvoke.return_value = mock_response

    system_prompt = "Test system prompt"
    chat_request = ChatRequest(messages=[MessageHistory(role="user", content="Hi")])

    response = await openai_service.process_chat_request(system_prompt, chat_request)

    assert response.message == "Hello!"
    assert response.usage == {}


@pytest.mark.asyncio
async def test_process_chat_request_error(openai_service, mock_client):
    """Test error handling during chat request processing."""
    mock_client.ainvoke.side_effect = Exception("API error")

    system_prompt = "Test system prompt"
    chat_request = ChatRequest(messages=[MessageHistory(role="user", content="Hello")])

    with pytest.raises(Exception, match="Failed to process chat request"):
        await openai_service.process_chat_request(system_prompt, chat_request)
        await openai_service.process_chat_request(system_prompt, chat_request)
        await openai_service.process_chat_request(system_prompt, chat_request)
