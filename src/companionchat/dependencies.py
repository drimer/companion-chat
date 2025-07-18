import os
from functools import lru_cache
from typing import Annotated, Any, AsyncGenerator, Callable, Dict

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
    session_params: Dict[str, Any] = {}

    # Check if we are running in the AWS Lambda environment.
    is_lambda_env = "AWS_LAMBDA_FUNCTION_NAME" in os.environ

    # For local development, use credentials from settings if available.
    # In the AWS Lambda environment, ALWAYS let boto3 find credentials
    # from the execution role, even if a .env file was packaged by mistake.
    if not is_lambda_env:
        if settings.AWS_REGION:
            session_params["region_name"] = settings.AWS_REGION

        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            print("Using credentials from settings for local development.")
            session_params["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            session_params["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

    print("session_params", session_params)
    session = aioboto3.session.Session(**session_params)

    client_params = {
        "config": Config(
            connect_timeout=5.0, read_timeout=10.0, retries={"max_attempts": 3}
        ),
    }
    if settings.AWS_ENDPOINT_URL:
        client_params["endpoint_url"] = settings.AWS_ENDPOINT_URL

    print("client_params", client_params)
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
