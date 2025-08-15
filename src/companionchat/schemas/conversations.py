from typing import List
from uuid import UUID
from datetime import datetime

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


class MessageHistory(BaseModel):
    """
    Represents a message in conversation history for client-side storage.
    """
    
    role: str = Field(..., description="The role of the message sender.")
    content: str = Field(..., description="The text content of the message.")


class BaseConversation(BaseModel):
    """
    Represents a conversation, including its unique ID and metadata.
    """

    id: UUID = Field(..., description="The unique identifier for the conversation.")


class ConversationCreateRequest(BaseModel):
    """
    Represents a request to create a new conversation.
    """
    pass  # No fields needed for now, using hardcoded values


class ConversationResponse(BaseConversation):
    """
    Represents a conversation response, including metadata.
    This is used for API responses.
    """

    system_prompt: str = Field(..., description="The system prompt for the conversation.")
    user_id: str = Field(..., description="The ID of the user who owns the conversation.")
    created_at: datetime = Field(..., description="When the conversation was created.")


class ChatRequest(BaseModel):
    """
    Represents a chat request with full conversation history.
    """
    
    messages: List[MessageHistory] = Field(
        ..., description="The full conversation history from the client."
    )


class ChatResponse(BaseModel):
    """
    Represents a response from the OpenAI chat completion.
    """
    
    message: str = Field(..., description="The AI assistant's response message.")
    usage: dict = Field(default_factory=dict, description="Token usage information.")
