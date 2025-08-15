from datetime import datetime, timezone
from uuid import uuid4

from types_aiobotocore_dynamodb import DynamoDBClient

from src.companionchat.db.models import Conversation, Message

# Hardcoded constants for now
DEFAULT_SYSTEM_PROMPT = "You are a language exchange student who speaks Japanese natively and wants to learn English. I am learning Japanese, and will help you improve your English as we speak."
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
            return Conversation(
                id=conversation_id,
                system_prompt=DEFAULT_SYSTEM_PROMPT,
                user_id=DEFAULT_USER_ID,
                created_at=created_at,
            )
        except Exception as e:
            raise Exception(f"Error creating conversation: {e}")

    async def get(self, conversation_id: str) -> Conversation:
        try:
            response = await self.client.get_item(
                TableName=self.table_name,
                Key={"id": {"S": conversation_id}},
            )
            item = response.get("Item")
            if not item:
                raise ValueError(f"Conversation with ID {conversation_id} not found.")

            return Conversation(
                id=item["id"]["S"],
                system_prompt=item["system_prompt"]["S"],
                user_id=item["user_id"]["S"],
                created_at=datetime.fromisoformat(item["created_at"]["S"]),
            )
        except ValueError:
            # Re-raise ValueError for not found cases
            raise
        except Exception as e:
            raise Exception(f"Error retrieving conversation: {e}")
