from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class BaseMessage(BaseModel):
    """
    Represents a single message within a conversation.
    """

    content: str = Field(..., description="The text content of the message.")


class MessageResponse(BaseMessage):
    """
    Represents a message with additional metadata such as role.
    """

    role: str = Field(
        ..., description="The role of the message sender (e.g., 'user', 'assistant')."
    )


class BaseConversation(BaseModel):
    """
    Represents a conversation, including its unique ID and all associated messages.
    """

    id: UUID = Field(..., description="The unique identifier for the conversation.")


class ConversationResponse(BaseConversation):
    """
    Represents a conversation response, including its unique ID and all associated messages.
    This is used for API responses.
    """

    messages: List[MessageResponse] = Field(
        [], description="A list of messages in the conversation."
    )
