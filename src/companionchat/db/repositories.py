from uuid import uuid4

from types_aiobotocore_dynamodb import DynamoDBClient

from companionchat.db.models import Conversation


class ConversationRepository:
    def __init__(self, client: DynamoDBClient):
        self.client = client

    async def create(self) -> Conversation:
        try:
            conversation_id = uuid4()
            await self.client.put_item(
                TableName="conversations",
                Item={
                    "id": {"S": str(conversation_id)},
                    "messages": {"L": []},
                },
            )
            return Conversation(
                id=conversation_id,
                messages=[],
            )
        except Exception as e:
            raise Exception(f"Error creating conversation: {e}")
