from fastapi import FastAPI
from mangum import Mangum

from src.companionchat.dependencies import ConversationRepositoryDep
from src.companionchat.schemas.conversations import BaseConversation

app = FastAPI(
    title="Companion Chat API",
    description="API for managing conversations with your companion.",
    version="0.1.0",
)


@app.post("/conversations", response_model=BaseConversation, status_code=201)
async def create_conversation(
    conversation_repository: ConversationRepositoryDep,
) -> BaseConversation:
    """
    Creates a new conversation and returns it.

    For now, this endpoint returns a hardcoded conversation with an empty
    message list. The ID is a fixed UUID to match the model's type.
    """
    conversation = await conversation_repository.create()
    return BaseConversation(id=conversation.id, messages=[])


# Create the handler that AWS Lambda will invoke
handler = Mangum(app, lifespan="off")
