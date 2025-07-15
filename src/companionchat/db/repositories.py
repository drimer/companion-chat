from uuid import UUID, uuid4

from types_aiobotocore_dynamodb import DynamoDBClient

from src.companionchat.schemas.conversations import BaseConversation


class ConversationRepository:
    def __init__(self, client: DynamoDBClient):
        self.client = client

    async def create(self) -> BaseConversation:
        try:
            response = await self.client.put_item(
                TableName="conversations",
                Item={
                    "id": {"S": str(uuid4())},
                    "messages": {"L": []},
                },
            )

            return BaseConversation(
                id=UUID(response["Attributes"]["id"]["S"]),
                messages=[],
            )
        except Exception as e:
            raise Exception(f"Error creating conversation: {e}")
