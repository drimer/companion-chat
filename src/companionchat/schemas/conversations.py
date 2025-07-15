from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class BaseMessage(BaseModel):
    """
    Represents a single message within a conversation.
    """

    role: str = Field(
        ..., description="The role of the message sender (e.g., 'user', 'assistant')."
    )
    content: str = Field(..., description="The text content of the message.")


class BaseConversation(BaseModel):
    """
    Represents a conversation, including its unique ID and all associated messages.
    """

    id: UUID = Field(..., description="The unique identifier for the conversation.")
    messages: List[BaseMessage] = Field(
        [], description="A list of messages in the conversation."
    )
