import logging
from typing import List

from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.companionchat.schemas.conversations import (
    ChatRequest,
    ChatResponse,
    MessageHistory,
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

        except Exception as e:
            logger.error(f"Error processing chat request: {e}")
            raise Exception(f"Failed to process chat request: {e}")

        except Exception as e:
            logger.error(f"Error processing chat request: {e}")
            raise Exception(f"Failed to process chat request: {e}")

        except Exception as e:
            logger.error(f"Error processing chat request: {e}")
            raise Exception(f"Failed to process chat request: {e}")
