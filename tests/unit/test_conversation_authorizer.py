from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from companionchat.authorization.conversation_authorizer import (
    ConversationAuthorizationService,
)
from companionchat.db.models import Conversation


@pytest.mark.asyncio
async def test_ensure_owner_returns_conversation_for_owner():
    conversation = Conversation(
        id=uuid4(),
        system_prompt="prompt",
        user_id="owner-sub",
        created_at=datetime.now(timezone.utc),
    )

    repository = AsyncMock()
    repository.get.return_value = conversation
    service = ConversationAuthorizationService(repository)

    result = await service.ensure_owner(str(conversation.id), "owner-sub")

    assert result is conversation
    repository.get.assert_awaited_once_with(str(conversation.id))


@pytest.mark.asyncio
async def test_ensure_owner_raises_for_different_user():
    conversation = Conversation(
        id=uuid4(),
        system_prompt="prompt",
        user_id="owner-sub",
        created_at=datetime.now(timezone.utc),
    )

    repository = AsyncMock()
    repository.get.return_value = conversation
    service = ConversationAuthorizationService(repository)

    with pytest.raises(HTTPException) as exc:
        await service.ensure_owner(str(conversation.id), "other-sub")

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_ensure_owner_raises_when_not_found():
    repository = AsyncMock()
    repository.get.return_value = None
    service = ConversationAuthorizationService(repository)

    with pytest.raises(HTTPException) as exc:
        await service.ensure_owner(str(uuid4()), "owner-sub")

    assert exc.value.status_code == 404
