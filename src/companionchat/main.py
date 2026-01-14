import os
from typing import Dict

from fastapi import FastAPI, HTTPException, logger
from mangum import Mangum

from companionchat.dependencies import (
    AuthenticatedSubDep,
    ConversationAuthorizerDep,
    ConversationRepositoryDep,
    OpenAIServiceDep,
    get_authenticated_sub,
)
from companionchat.schemas.conversations import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
)
from companionchat.settings import configure_logging

app = FastAPI(
    title="Companion Chat API",
    description="API for managing conversations with your companion.",
    version="0.1.0",
)

configure_logging()

_local_sub = os.getenv("COMPANIONCHAT_LOCAL_SUB")
if _local_sub:

    async def _local_sub_override() -> str:
        return _local_sub

    app.dependency_overrides[get_authenticated_sub] = _local_sub_override


@app.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    conversation_repository: ConversationRepositoryDep,
    openai_service: OpenAIServiceDep,
    owner_sub: AuthenticatedSubDep,
) -> ConversationResponse:
    """
    Creates a new conversation and returns it.

    Creates a conversation with hardcoded system prompt and user ID.
    The conversation metadata (ID, system prompt, user ID, created_at) is stored,
    but no messages are stored in the database.
    """
    conversation = await conversation_repository.create(owner_sub)

    logger.logger.info(f"Created a new conversation with ID: {conversation.id}")

    try:
        initial_message = await openai_service.generate_initial_message(
            conversation.system_prompt
        )
    except Exception:
        logger.logger.exception(
            f"Failed generating initial message for conversation {conversation.id}"
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate initial assistant message.",
        )

    logger.logger.info(f"initial_message type: {type(initial_message)}")
    logger.logger.info(f"initial_message content: {initial_message.content}")
    logger.logger.info(f"initial_message role: {initial_message.role}")

    response = ConversationResponse(
        id=conversation.id,
        system_prompt=conversation.system_prompt,
        user_id=conversation.user_id,
        created_at=conversation.created_at,
        messages=[initial_message],
    )

    return response


@app.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    conversation_authorizer: ConversationAuthorizerDep,
    owner_sub: AuthenticatedSubDep,
) -> ConversationResponse:
    """
    Retrieves a conversation by its ID.

    This endpoint fetches the conversation metadata identified by `conversation_id`
    and returns it. If the conversation does not exist, an error will be raised.
    Note: This only returns metadata, not conversation messages.
    """
    logger.logger.info(f"Retrieving conversation with ID: {conversation_id}")

    conversation = await conversation_authorizer.ensure_owner(
        conversation_id, owner_sub
    )

    return ConversationResponse(
        id=conversation.id,
        system_prompt=conversation.system_prompt,
        user_id=conversation.user_id,
        created_at=conversation.created_at,
        messages=[],
    )


@app.post("/conversations/{conversation_id}/chat")
async def chat_with_conversation(
    conversation_id: str,
    chat_request: ChatRequest,
    openai_service: OpenAIServiceDep,
    conversation_authorizer: ConversationAuthorizerDep,
    owner_sub: AuthenticatedSubDep,
) -> ChatResponse:
    """
    Process a chat request with the full conversation history.

    This endpoint accepts the complete conversation history from the client
    and sends it to OpenAI for processing. Returns the AI assistant's response.
    """
    conversation = await conversation_authorizer.ensure_owner(
        conversation_id, owner_sub
    )

    response = await openai_service.process_chat_request(
        system_prompt=conversation.system_prompt, chat_request=chat_request
    )

    return response


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# Create the handler that AWS Lambda will invoke
handler = Mangum(app, lifespan="off")
handler = Mangum(app, lifespan="off")
handler = Mangum(app, lifespan="off")
