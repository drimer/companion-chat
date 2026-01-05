from datetime import datetime, timezone
from typing import Optional, Union
from uuid import UUID, uuid4

from fastapi import logger
from types_aiobotocore_dynamodb import DynamoDBClient

from src.companionchat.db.models import Conversation

# Hardcoded constants for now
DEFAULT_SYSTEM_PROMPT = """
I need you to act as a Japanese language teacher who is pretending to be in real-life, day-to-day scenario with me, so that I can practice talking in Japanese.

You pick a random scenario, for example a person working on a shop till about to take my purchase, a hotel receptionist greeting me for check-in, or any other scenario you can imagine.

I need you to first describe the scenario to me, and open up the conversation in Japanese.

Each time I you respond to something I say, I need you to add notes at the bottom of your messages informing me about mistakes I make, or suggestions to improve the way I say things.

If you use any Japanese kanjis, please provide the reading in hiragana at the bottom of your message as a footnote.
"""
DEFAULT_USER_ID = "default-user-123"  # Temporary until authentication is implemented


class ConversationRepository:
    def __init__(self, client: DynamoDBClient, table_name: str):
        self.client = client
        self.table_name = table_name

    async def create(self) -> Conversation:
        try:
            conversation_id = uuid4()
            created_at = datetime.now(timezone.utc)

            await self.client.put_item(
                TableName=self.table_name,
                Item={
                    "id": {"S": str(conversation_id)},
                    "system_prompt": {"S": DEFAULT_SYSTEM_PROMPT},
                    "user_id": {"S": DEFAULT_USER_ID},
                    "created_at": {"S": created_at.isoformat()},
                },
            )

            logger.logger.info(
                f"Created conversation with ID: {conversation_id} and default prompt"
            )
            return Conversation(
                id=conversation_id,
                system_prompt=DEFAULT_SYSTEM_PROMPT,
                user_id=DEFAULT_USER_ID,
                created_at=created_at,
            )
        except Exception as e:
            raise Exception(f"Error creating conversation: {e}")

    async def get(self, conversation_id: Union[str, UUID]) -> Optional[Conversation]:
        try:
            # Convert UUID to string if necessary
            id_str = str(conversation_id)

            response = await self.client.get_item(
                TableName=self.table_name,
                Key={"id": {"S": id_str}},
            )
            item = response.get("Item")
            if not item:
                return None  # Return None instead of raising ValueError

            return Conversation(
                id=UUID(item["id"]["S"]),  # Convert string back to UUID
                system_prompt=item["system_prompt"]["S"],
                user_id=item["user_id"]["S"],
                created_at=datetime.fromisoformat(item["created_at"]["S"]),
            )
        except Exception as e:
            raise Exception(f"Error retrieving conversation: {e}")
