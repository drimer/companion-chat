"""Authorization helpers for conversation resources."""

from fastapi import HTTPException

from companionchat.db.models import Conversation
from companionchat.db.repositories import ConversationRepository


class ConversationAuthorizationService:
    """Encapsulates ownership checks for conversation entities."""

    def __init__(self, conversation_repository: ConversationRepository):
        self._conversation_repository = conversation_repository

    async def ensure_owner(self, conversation_id: str, owner_sub: str) -> Conversation:
        """Return the conversation when the caller owns it, raise otherwise."""
        try:
            conversation = await self._conversation_repository.get(conversation_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Internal server error: {exc}"
            ) from exc

        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")

        if conversation.user_id != owner_sub:
            raise HTTPException(status_code=403, detail="Forbidden")

        return conversation
