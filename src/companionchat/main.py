from typing import List
from uuid import UUID

from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel, Field


class Message(BaseModel):
    """
    Represents a single message within a conversation.
    """

    role: str = Field(
        ..., description="The role of the message sender (e.g., 'user', 'assistant')."
    )
    content: str = Field(..., description="The text content of the message.")


class Conversation(BaseModel):
    """
    Represents a conversation, including its unique ID and all associated messages.
    """

    id: UUID = Field(..., description="The unique identifier for the conversation.")
    messages: List[Message] = Field(
        [], description="A list of messages in the conversation."
    )


# --- FastAPI Application ---

app = FastAPI(
    title="Companion Chat API",
    description="API for managing conversations with your companion.",
    version="0.1.0",
)


@app.post("/conversations", response_model=Conversation, status_code=201)
async def create_conversation() -> Conversation:
    """
    Creates a new conversation and returns it.

    For now, this endpoint returns a hardcoded conversation with an empty
    message list. The ID is a fixed UUID to match the model's type.
    """
    return Conversation(id=UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479"))


# Create the handler that AWS Lambda will invoke
handler = Mangum(app, lifespan="off")
