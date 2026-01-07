"""Authorization helpers for conversation resources."""

from companionchat.db.models import Conversation


class ConversationAuthorizationService:
    """Encapsulates ownership checks for conversation entities."""

    def ensure_owner(self, conversation: Conversation, owner_sub: str) -> None:
        """Raise PermissionError when the user does not own the conversation."""
        if conversation.user_id != owner_sub:
            raise PermissionError("Conversation ownership mismatch")
