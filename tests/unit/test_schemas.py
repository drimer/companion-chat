from datetime import datetime
from uuid import uuid4


from src.companionchat.schemas.conversations import (
    ChatRequest,
    ChatResponse,
    ConversationCreateRequest,
    ConversationResponse,
    MessageHistory,
)


def test_conversation_create_request():
    """Test ConversationCreateRequest schema."""
    request = ConversationCreateRequest()
    assert request is not None


def test_conversation_response():
    """Test ConversationResponse schema."""
    conversation_id = uuid4()
    created_at = datetime.now()

    response = ConversationResponse(
        id=conversation_id,
        system_prompt="Test system prompt",
        user_id="test-user",
        created_at=created_at,
    )

    assert response.id == conversation_id
    assert response.system_prompt == "Test system prompt"
    assert response.user_id == "test-user"
    assert response.created_at == created_at


def test_message_history():
    """Test MessageHistory schema."""
    message = MessageHistory(role="user", content="Hello, how are you?")

    assert message.role == "user"
    assert message.content == "Hello, how are you?"


def test_chat_request():
    """Test ChatRequest schema."""
    messages = [
        MessageHistory(role="user", content="Hello"),
        MessageHistory(role="assistant", content="Hi there!"),
        MessageHistory(role="user", content="How are you?"),
    ]

    request = ChatRequest(messages=messages)

    assert len(request.messages) == 3
    assert request.messages[0].role == "user"
    assert request.messages[1].role == "assistant"
    assert request.messages[2].content == "How are you?"


def test_chat_response():
    """Test ChatResponse schema."""
    usage = {"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}

    response = ChatResponse(message="I'm doing well, thank you!", usage=usage)

    assert response.message == "I'm doing well, thank you!"
    assert response.usage["total_tokens"] == 25


def test_chat_response_empty_usage():
    """Test ChatResponse with empty usage."""
    response = ChatResponse(message="Hello!")

    assert response.message == "Hello!"
    assert response.usage == {}
    assert response.usage == {}
    assert response.usage == {}
