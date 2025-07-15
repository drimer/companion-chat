from contextlib import asynccontextmanager
from uuid import UUID

import aioboto3
from fastapi import FastAPI
from mangum import Mangum

from src.companionchat.dependencies import ConversationRepositoryDep
from src.companionchat.schemas.conversations import BaseConversation


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.dynamodb_session = aioboto3.session.Session(
        aws_access_key_id="dummy",  # TODO: use real one
        aws_secret_access_key="dummy",  # TODO: use real one
        region_name="us-east-1",  # TODO: use real one
    )
    yield


app = FastAPI(
    title="Companion Chat API",
    description="API for managing conversations with your companion.",
    version="0.1.0",
    lifespan=lifespan,
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
    conversation_repository.create()
    return BaseConversation(id=UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479"))


# Create the handler that AWS Lambda will invoke
handler = Mangum(app, lifespan="off")
