from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from companionchat.db.repositories import DEFAULT_SYSTEM_PROMPT, ConversationRepository

OWNER_SUB = "user-sub-123"


@pytest.fixture
def mock_dynamodb_client():
    return AsyncMock()


@pytest.fixture
def repository(mock_dynamodb_client):
    return ConversationRepository(mock_dynamodb_client, "test-table")


@pytest.mark.asyncio
async def test_create_conversation(repository, mock_dynamodb_client):
    mock_dynamodb_client.put_item.return_value = {}

    conversation = await repository.create(OWNER_SUB)

    assert isinstance(conversation.id, UUID)
    assert conversation.system_prompt == DEFAULT_SYSTEM_PROMPT
    assert conversation.user_id == OWNER_SUB
    assert isinstance(conversation.created_at, datetime)

    mock_dynamodb_client.put_item.assert_called_once()
    call_args = mock_dynamodb_client.put_item.call_args
    item = call_args[1]["Item"]
    assert item["system_prompt"]["S"] == DEFAULT_SYSTEM_PROMPT
    assert item["user_id"]["S"] == OWNER_SUB


@pytest.mark.asyncio
async def test_get_conversation_success(repository, mock_dynamodb_client):
    conversation_id = "550e8400-e29b-41d4-a716-446655440000"
    created_at = datetime.now(timezone.utc)

    mock_dynamodb_client.get_item.return_value = {
        "Item": {
            "id": {"S": conversation_id},
            "system_prompt": {"S": DEFAULT_SYSTEM_PROMPT},
            "user_id": {"S": OWNER_SUB},
            "created_at": {"S": created_at.isoformat()},
        }
    }

    conversation = await repository.get(conversation_id)

    assert conversation is not None
    assert str(conversation.id) == conversation_id
    assert conversation.user_id == OWNER_SUB


@pytest.mark.asyncio
async def test_get_conversation_not_found(repository, mock_dynamodb_client):
    mock_dynamodb_client.get_item.return_value = {}

    result = await repository.get("missing")
    assert result is None


@pytest.mark.asyncio
async def test_create_conversation_error(repository, mock_dynamodb_client):
    mock_dynamodb_client.put_item.side_effect = Exception("DynamoDB error")

    with pytest.raises(Exception, match="Error creating conversation"):
        await repository.create(OWNER_SUB)


@pytest.mark.asyncio
async def test_get_conversation_error(repository, mock_dynamodb_client):
    mock_dynamodb_client.get_item.side_effect = Exception("DynamoDB error")

    with pytest.raises(Exception, match="Error retrieving conversation"):
        await repository.get("test-id")


@pytest.mark.asyncio
async def test_list_for_user(repository, mock_dynamodb_client):
    created_at = datetime.now(timezone.utc)
    mock_dynamodb_client.query.return_value = {
        "Items": [
            {
                "id": {"S": "a1111111-b222-c333-d444-eeeeeeeeeeee"},
                "system_prompt": {"S": DEFAULT_SYSTEM_PROMPT},
                "user_id": {"S": OWNER_SUB},
                "created_at": {"S": created_at.isoformat()},
            }
        ]
    }

    items = await repository.list_for_user(OWNER_SUB)

    assert len(items) == 1
    assert items[0].user_id == OWNER_SUB

    mock_dynamodb_client.query.assert_called_once_with(
        TableName="test-table",
        IndexName="user_id-index",
        KeyConditionExpression="user_id = :owner",
        ExpressionAttributeValues={":owner": {"S": OWNER_SUB}},
    )
