from fastapi import FastAPI, HTTPException
from mangum import Mangum

from src.companionchat.dependencies import ConversationRepositoryDep, OpenAIServiceDep
from src.companionchat.schemas.conversations import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
)

app = FastAPI(
    title="Companion Chat API",
    description="API for managing conversations with your companion.",
    version="0.1.0",
)


@app.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    conversation_repository: ConversationRepositoryDep,
) -> ConversationResponse:
    """
    Creates a new conversation and returns it.

    Creates a conversation with hardcoded system prompt and user ID.
    The conversation metadata (ID, system prompt, user ID, created_at) is stored,
    but no messages are stored in the database.
    """
    conversation = await conversation_repository.create()
    return ConversationResponse(
        id=conversation.id,
        system_prompt=conversation.system_prompt,
        user_id=conversation.user_id,
        created_at=conversation.created_at,
    )


@app.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    conversation_repository: ConversationRepositoryDep,
) -> ConversationResponse:
    """
    Retrieves a conversation by its ID.

    This endpoint fetches the conversation metadata identified by `conversation_id`
    and returns it. If the conversation does not exist, an error will be raised.
    Note: This only returns metadata, not conversation messages.
    """
    try:
        conversation = await conversation_repository.get(conversation_id)
        return ConversationResponse(
            id=conversation.id,
            system_prompt=conversation.system_prompt,
            user_id=conversation.user_id,
            created_at=conversation.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.post("/conversations/{conversation_id}/chat")
async def chat_with_conversation(
    conversation_id: str,
    chat_request: ChatRequest,
    conversation_repository: ConversationRepositoryDep,
    openai_service: OpenAIServiceDep,
) -> ChatResponse:
    """
    Process a chat request with the full conversation history.

    This endpoint accepts the complete conversation history from the client
    and sends it to OpenAI for processing. Returns the AI assistant's response.
    """
    try:
        # Verify conversation exists and get system prompt
        conversation = await conversation_repository.get(conversation_id)

        # Process chat request with OpenAI
        response = await openai_service.process_chat_request(
            system_prompt=conversation.system_prompt, chat_request=chat_request
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Create the handler that AWS Lambda will invoke
handler = Mangum(app, lifespan="off")
