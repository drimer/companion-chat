from functools import lru_cache
from typing import Annotated, Any, AsyncGenerator, Callable

from botocore.config import Config
from fastapi import Depends, Request
from types_aiobotocore_dynamodb import DynamoDBClient

from src.companionchat.db.repositories import ConversationRepository
from src.companionchat.settings import get_settings

DbContextDependency = Callable[..., AsyncGenerator[Any, None]]


def get_db_context() -> DbContextDependency:
    async def get_dynamo_context(
        request: Request,
    ) -> AsyncGenerator[DynamoDBClient, None]:
        settings = get_settings()

        # Get the session from app state
        session = request.app.state.dynamodb_session

        # Create a client for this request using the shared session
        async with session.client(
            "dynamodb",
            endpoint_url=settings.AWS_ENDPOINT_URL,
            config=Config(
                connect_timeout=5.0, read_timeout=10.0, retries={"max_attempts": 3}
            ),
        ) as dynamodb_client:
            dynamodb_client: DynamoDBClient
            yield dynamodb_client

    return get_dynamo_context


DB_CONTEXT = get_db_context()


@lru_cache
def get_conversation_repository(
    db: DynamoDBClient = Depends(DB_CONTEXT),
) -> ConversationRepository:
    return ConversationRepository(db)


ConversationRepositoryDep = Annotated[
    ConversationRepository, Depends(get_conversation_repository)
]
