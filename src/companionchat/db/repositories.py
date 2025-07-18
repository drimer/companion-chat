from uuid import uuid4

from types_aiobotocore_dynamodb import DynamoDBClient

from src.companionchat.db.models import Conversation, Message


class ConversationRepository:
    def __init__(self, client: DynamoDBClient, table_name: str):
        self.client = client
        self.table_name = table_name

    async def create(self) -> Conversation:
        try:
            conversation_id = uuid4()
            await self.client.put_item(
                TableName=self.table_name,
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

    async def get(self, conversation_id: str) -> Conversation:
        try:
            response = await self.client.get_item(
                TableName=self.table_name,
                Key={"id": {"S": conversation_id}},
            )
            item = response.get("Item")
            if not item:
                raise ValueError(f"Conversation with ID {conversation_id} not found.")

            raw_messages = item.get("messages", {"L": []})["L"]
            messages = [
                Message(role=msg["M"]["role"]["S"], content=msg["M"]["content"]["S"])
                for msg in raw_messages
            ]

            return Conversation(
                id=item["id"]["S"],
                messages=messages,
            )
        except Exception as e:
            raise Exception(f"Error retrieving conversation: {e}")

    async def store_new_message(self, conversation_id: str, message: str) -> None:
        try:
            await self.client.update_item(
                TableName=self.table_name,
                Key={"id": {"S": conversation_id}},
                UpdateExpression="SET messages = list_append(messages, :message)",
                ExpressionAttributeValues={
                    ":message": {
                        "L": [{"M": {"role": {"S": "user"}, "content": {"S": message}}}]
                    }
                },
            )
        except Exception as e:
            raise Exception(f"Error storing new message: {e}")
