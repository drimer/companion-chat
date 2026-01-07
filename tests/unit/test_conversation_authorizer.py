from datetime import datetime, timezone
from uuid import uuid4

import pytest

from companionchat.authorization.conversation_authorizer import (
    ConversationAuthorizationService,
)
from companionchat.db.models import Conversation


def test_ensure_owner_allows_matching_user():
    conversation = Conversation(
        id=uuid4(),
        system_prompt="prompt",
        user_id="owner-sub",
        created_at=datetime.now(timezone.utc),
    )

    service = ConversationAuthorizationService()
    service.ensure_owner(conversation, "owner-sub")


def test_ensure_owner_raises_for_different_user():
    conversation = Conversation(
        id=uuid4(),
        system_prompt="prompt",
        user_id="owner-sub",
        created_at=datetime.now(timezone.utc),
    )

    service = ConversationAuthorizationService()

    with pytest.raises(PermissionError):
        service.ensure_owner(conversation, "other-sub")
