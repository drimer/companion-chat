from functools import lru_cache
from typing import Annotated, Any, AsyncGenerator, Callable

import aioboto3
from botocore.config import Config
from fastapi import Depends, Request
from types_aiobotocore_dynamodb import DynamoDBClient

from src.companionchat.db.repositories import ConversationRepository
from src.companionchat.settings import get_settings

DbContextDependency = Callable[..., AsyncGenerator[Any, None]]


def create_dynamodb_client_context():
    """Creates a context manager for a DynamoDB client."""
    settings = get_settings()
    # Let aioboto3 find credentials from the environment (preferred for Lambda)
    # or use the ones from settings (useful for local development).
    session_params = {}
    if settings.AWS_REGION:
        session_params["region_name"] = settings.AWS_REGION
    if settings.AWS_ACCESS_KEY_ID:
        session_params["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
    if settings.AWS_SECRET_ACCESS_KEY:
        session_params["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

    session = aioboto3.session.Session(**session_params)

    client_params = {
        "config": Config(
            connect_timeout=5.0, read_timeout=10.0, retries={"max_attempts": 3}
        ),
    }
    if settings.AWS_ENDPOINT_URL:
        client_params["endpoint_url"] = settings.AWS_ENDPOINT_URL

    return session.client("dynamodb", **client_params)


def get_db_context() -> DbContextDependency:
    async def get_dynamo_context(
        request: Request,
    ) -> AsyncGenerator[DynamoDBClient, None]:
        async with create_dynamodb_client_context() as dynamodb_client:
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
