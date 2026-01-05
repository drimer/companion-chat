import logging
from typing import List

from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.companionchat.schemas.conversations import (
    ChatRequest,
    ChatResponse,
    MessageHistory,
    MessageResponse,
)

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for handling OpenAI chat completions using Langchain."""

    def __init__(self, client: ChatOpenAI):
        self.client = client

    def _convert_messages_to_langchain(
        self, system_prompt: str, messages: List[MessageHistory]
    ) -> List[BaseMessage]:
        """Convert our message format to Langchain message format."""
        langchain_messages = [SystemMessage(content=system_prompt)]

        for message in messages:
            if message.role == "user":
                langchain_messages.append(HumanMessage(content=message.content))
            elif message.role == "assistant":
                langchain_messages.append(AIMessage(content=message.content))
            else:
                logger.warning(f"Unknown message role: {message.role}")

        return langchain_messages

    async def generate_initial_message(self, system_prompt: str) -> MessageResponse:
        """Generate the first assistant message for a newly created conversation."""
        try:
            logger.info("Generating initial assistant message for new conversation")

            response = await self.client.ainvoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(
                        content=(
                            "Initiate the scenario described in the system prompt and "
                            "greet me naturally in Japanese before providing guidance."
                        )
                    ),
                ]
            )

            logger.info("Initial assistant message generated successfully")
            return MessageResponse(role="assistant", content=response.content)

        except Exception as exc:  # pragma: no cover - ensures consistent error surface
            logger.error(f"Error generating initial assistant message: {exc}")
            raise Exception(f"Failed to generate initial assistant message: {exc}")

    async def process_chat_request(
        self, system_prompt: str, chat_request: ChatRequest
    ) -> ChatResponse:
        """Process a chat request and return the AI response."""
        try:
            # Convert messages to Langchain format
            langchain_messages = self._convert_messages_to_langchain(
                system_prompt, chat_request.messages
            )

            logger.info(
                f"Processing chat request with {len(chat_request.messages)} messages"
            )

            # Get response from OpenAI
            response = await self.client.ainvoke(langchain_messages)

            # Extract usage information if available
            usage_info = {}
            if hasattr(response, "response_metadata") and response.response_metadata:
                token_usage = response.response_metadata.get("token_usage", {})
                usage_info = {
                    "prompt_tokens": token_usage.get("prompt_tokens", 0),
                    "completion_tokens": token_usage.get("completion_tokens", 0),
                    "total_tokens": token_usage.get("total_tokens", 0),
                }

            logger.info(f"OpenAI response received. Usage: {usage_info}")

            return ChatResponse(message=response.content, usage=usage_info)

        except Exception as exc:  # pragma: no cover - ensures consistent error surface
            logger.error(f"Error processing chat request: {exc}")
            raise Exception(f"Failed to process chat request: {exc}")
