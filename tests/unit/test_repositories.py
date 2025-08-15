import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from uuid import UUID

from src.companionchat.db.repositories import ConversationRepository, DEFAULT_SYSTEM_PROMPT, DEFAULT_USER_ID
from src.companionchat.db.models import Conversation


@pytest.fixture
def mock_dynamodb_client():
    """Create a mock DynamoDB client."""
    return AsyncMock()


@pytest.fixture
def repository(mock_dynamodb_client):
    """Create a ConversationRepository instance with mocked client."""
    return ConversationRepository(mock_dynamodb_client, "test-table")


@pytest.mark.asyncio
async def test_create_conversation(repository, mock_dynamodb_client):
    """Test creating a new conversation."""
    mock_dynamodb_client.put_item.return_value = {}
    
    conversation = await repository.create()
    
    assert isinstance(conversation.id, UUID)
    assert conversation.system_prompt == DEFAULT_SYSTEM_PROMPT
    assert conversation.user_id == DEFAULT_USER_ID
    assert isinstance(conversation.created_at, datetime)
    
    mock_dynamodb_client.put_item.assert_called_once()
    call_args = mock_dynamodb_client.put_item.call_args
    assert call_args[1]["TableName"] == "test-table"
    
    item = call_args[1]["Item"]
    assert "id" in item
    assert item["system_prompt"]["S"] == DEFAULT_SYSTEM_PROMPT
    assert item["user_id"]["S"] == DEFAULT_USER_ID
    assert "created_at" in item


@pytest.mark.asyncio
async def test_get_conversation_success(repository, mock_dynamodb_client):
    """Test successfully retrieving a conversation."""
    conversation_id = "test-conversation-id"
    created_at = datetime.now(timezone.utc)
    
    mock_dynamodb_client.get_item.return_value = {
        "Item": {
            "id": {"S": conversation_id},
            "system_prompt": {"S": DEFAULT_SYSTEM_PROMPT},
            "user_id": {"S": DEFAULT_USER_ID},
            "created_at": {"S": created_at.isoformat()},
        }
    }
    
    conversation = await repository.get(conversation_id)
    
    assert conversation.id == conversation_id
    assert conversation.system_prompt == DEFAULT_SYSTEM_PROMPT
    assert conversation.user_id == DEFAULT_USER_ID
    assert conversation.created_at == created_at
    
    mock_dynamodb_client.get_item.assert_called_once_with(
        TableName="test-table",
        Key={"id": {"S": conversation_id}},
    )


@pytest.mark.asyncio
async def test_get_conversation_not_found(repository, mock_dynamodb_client):
    """Test retrieving a conversation that doesn't exist."""
    conversation_id = "non-existent-id"
    mock_dynamodb_client.get_item.return_value = {}
    
    with pytest.raises(ValueError, match=f"Conversation with ID {conversation_id} not found"):
        await repository.get(conversation_id)


@pytest.mark.asyncio
async def test_create_conversation_error(repository, mock_dynamodb_client):
    """Test error handling during conversation creation."""
    mock_dynamodb_client.put_item.side_effect = Exception("DynamoDB error")
    
    with pytest.raises(Exception, match="Error creating conversation"):
        await repository.create()


@pytest.mark.asyncio
async def test_get_conversation_error(repository, mock_dynamodb_client):
    """Test error handling during conversation retrieval."""
    mock_dynamodb_client.get_item.side_effect = Exception("DynamoDB error")
    
    with pytest.raises(Exception, match="Error retrieving conversation"):
        await repository.get("test-id")
