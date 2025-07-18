from typing import Annotated

from fastapi import Body, FastAPI
from mangum import Mangum

from src.companionchat.dependencies import ConversationRepositoryDep
from src.companionchat.schemas.conversations import (
    BaseConversation,
    BaseMessage,
    ConversationResponse,
    MessageResponse,
)

app = FastAPI(
    title="Companion Chat API",
    description="API for managing conversations with your companion.",
    version="0.1.0",
)


@app.post("/conversations", response_model=BaseConversation, status_code=201)
async def create_conversation(
    conversation_repository: ConversationRepositoryDep,
) -> ConversationResponse:
    """
    Creates a new conversation and returns it.

    For now, this endpoint returns a hardcoded conversation with an empty
    message list. The ID is a fixed UUID to match the model's type.
    """
    conversation = await conversation_repository.create()
    return ConversationResponse(id=conversation.id, messages=[])


@app.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    conversation_repository: ConversationRepositoryDep,
) -> ConversationResponse:
    """
    Retrieves a conversation by its ID.

    This endpoint fetches the conversation identified by `conversation_id`
    and returns it. If the conversation does not exist, an error will be raised.
    """
    conversation = await conversation_repository.get(conversation_id)

    return ConversationResponse(
        id=conversation.id,
        messages=[
            MessageResponse(role=msg.role, content=msg.content)
            for msg in conversation.messages
        ],
    )


@app.post("/conversations/{conversation_id}/messages", status_code=201)
async def store_new_message(
    conversation_id: str,
    message: Annotated[BaseMessage, Body(description="The message content to store.")],
    conversation_repository: ConversationRepositoryDep,
) -> None:
    """
    Stores a new message in the specified conversation.

    This endpoint adds a new message to the conversation identified by
    `conversation_id`. The message is expected to be a string.
    """
    print("Storing new message:", message)
    await conversation_repository.store_new_message(conversation_id, message.content)


@app.get("/conversations/{conversation_id}/messages", status_code=200)
async def get_conversation_messages(
    conversation_id: str,
    conversation_repository: ConversationRepositoryDep,
) -> list[MessageResponse]:
    """
    Retrieves all messages from a conversation by its ID.

    This endpoint fetches all messages associated with the conversation
    identified by `conversation_id` and returns them. If the conversation
    does not exist, an error will be raised.
    """
    conversation = await conversation_repository.get(conversation_id)
    if not conversation:
        raise ValueError(f"Conversation with ID {conversation_id} not found.")
    return [
        MessageResponse(role=msg.role, content=msg.content)
        for msg in conversation.messages
    ]


# Create the handler that AWS Lambda will invoke
handler = Mangum(app, lifespan="off")
