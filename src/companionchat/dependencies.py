from functools import lru_cache
from typing import Annotated, Any, AsyncGenerator, Callable, Dict

import aioboto3
from botocore.config import Config
from fastapi import Depends, Request
from langchain_openai import ChatOpenAI
from types_aiobotocore_dynamodb import DynamoDBClient

from src.companionchat.db.repositories import ConversationRepository
from src.companionchat.services.openai_service import OpenAIService
from src.companionchat.settings import get_settings

DbContextDependency = Callable[..., AsyncGenerator[Any, None]]


def create_dynamodb_client_context():
    """Creates a context manager for a DynamoDB client."""
    settings = get_settings()
    session_params: Dict[str, Any] = {}

    # For local development, use credentials from settings if available.
    # In the AWS Lambda environment, ALWAYS let boto3 find credentials
    # from the execution role, even if a .env file was packaged by mistake.
    if not settings.is_aws_lambda_environment:
        if settings.AWS_REGION:
            session_params["region_name"] = settings.AWS_REGION

        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            print("Using credentials from settings for local development.")
            session_params["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
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
    return ConversationRepository(db, get_settings().DB_CONVERSATIONS_TABLE_NAME)


ConversationRepositoryDep = Annotated[
    ConversationRepository, Depends(get_conversation_repository)
]


@lru_cache
def get_openai_client() -> ChatOpenAI:
    """Get the ChatOpenAI client instance."""
    settings = get_settings()
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set in environment variables")
    return ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL,
        max_tokens=settings.MAX_TOKENS,
        temperature=0.7,
    )


def get_openai_service(
    client: ChatOpenAI = Depends(get_openai_client),
) -> OpenAIService:
    """Get the OpenAI service instance."""
    return OpenAIService(client)


OpenAIServiceDep = Annotated[OpenAIService, Depends(get_openai_service)]
