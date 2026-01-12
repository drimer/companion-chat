from functools import lru_cache
from itertools import count
from typing import Annotated, Any, AsyncGenerator, Callable, Dict

import aioboto3
from botocore.config import Config
from fastapi import Depends, HTTPException, Request, status
from langchain_openai import ChatOpenAI
from types_aiobotocore_dynamodb import DynamoDBClient

from companionchat.authorization.conversation_authorizer import (
    ConversationAuthorizationService,
)
from companionchat.authorization.jwt import extract_authorizer_claims
from companionchat.db.repositories import ConversationRepository
from companionchat.services.openai_service import MockOpenAIService, OpenAIService
from companionchat.settings import get_settings

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
    return ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL,
        max_tokens=settings.MAX_TOKENS,
        temperature=0.7,
    )


def get_openai_service() -> OpenAIService:
    """Get the OpenAI service instance."""
    settings = get_settings()

    if settings.USE_MOCK_OPENAI:
        return MockOpenAIService()

    client = get_openai_client()
    return OpenAIService(client)


OpenAIServiceDep = Annotated[OpenAIService, Depends(get_openai_service)]


def get_conversation_authorization_service(
    conversation_repository: ConversationRepository = Depends(
        get_conversation_repository
    ),
) -> ConversationAuthorizationService:
    return ConversationAuthorizationService(conversation_repository)


ConversationAuthorizerDep = Annotated[
    ConversationAuthorizationService, Depends(get_conversation_authorization_service)
]


def _get_fake_authenticated_sub_for_local(request: Request):
    auth_header = request.headers.get("authorization")
    if isinstance(auth_header, str) and auth_header.lower().startswith("bearer "):
        token = auth_header[7:].strip()
        if token:
            request.state.auth_claims = {
                "sub": token,
                "source": "local-bearer",
                "token": token,
            }
            return token


async def get_authenticated_sub(request: Request) -> str:
    settings = get_settings()

    print("===================== request.headers =====================")
    for key, value in request.headers.items():
        print(f"{key}: {value}")
    print("==========================================================")

    if settings.is_aws_lambda_environment:
        claims = extract_authorizer_claims(request)
        if claims and isinstance(claims.get("sub"), str):
            request.state.auth_claims = claims
            return claims["sub"]

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authenticated user context from API Gateway authorizer",
        )

    else:
        local_token = _get_fake_authenticated_sub_for_local(request)
        if local_token:
            return local_token

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header for local development",
        )


_local_bearer_counter = count(1)


AuthenticatedSubDep = Annotated[str, Depends(get_authenticated_sub)]
