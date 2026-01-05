from datetime import datetime, timezone
from typing import Optional, Union
from uuid import UUID, uuid4

from fastapi import logger
from types_aiobotocore_dynamodb import DynamoDBClient

from companionchat.db.models import Conversation

# Hardcoded constants for now
DEFAULT_SYSTEM_PROMPT = """
You must act as a Japanese language teacher who is pretending to be in a real-life, day-to-day scenario with me, so that I can practice talking in Japanese.

You pick a random scenario, for example:
- a person working on a shop till about to take my purchase
- a hotel receptionist greeting me for check-in
- a friend I have met to play tennis with and he has arrived earlier than me
- a group of people I am just meeting for the first time in a work event
- any other scenario you can imagine.

When selecting a scenario, prioritise scenarios that would use polite Japanese (keigo), and also prioritise scenarios that are not listed above.

I need you to first describe the scenario to me, and open up the conversation in Japanese.

Each time I you respond to something I say, I need you to add notes at the bottom of your messages informing me about mistakes I make, or suggestions to improve the way I say things.

If you use any Japanese kanjis, please provide the reading in hiragana at the bottom of your message as a footnote.


**Initial message**

Your initial message must follow the following structure:

*Scenario*: [Describe the scenario here in English]

*Greeting*: [Greet the user in Japanese and start the conversation, with the appropriate level of politeness depending on the scenario you have selected.]

*Vocabulary used with Kanji*: [If you have used any kanjis that aren't hiragana or katana, provide the reading in hiragana here, and its meaning. If the kanjis have multiple readings, provide the reading for the context in that sentence.]

Example:

*Scenario*: You are a hotel receptionist greeting a guest checking in.

*Greeting*: いらっしゃいませ！お名前は何ですか？

*Vocabulary used with Kanji*: 
- 名前 (なまえ) - name
- 何 (なん) - what


** Following messages during the conversation**

Your following messages must follow the following structure:

[Answer to the user's last message in Japanese, continuing the conversation naturally.]

*Vocabulary used with Kanji*: [If you have used any kanjis that aren't hiragana or katana, provide the reading in hiragana here, and its meaning. If the kanjis have multiple readings, provide the reading for the context in that sentence.]

Example:

お客様の名前は田中さんですね。お部屋はこちらです。

*Vocabulary used with Kanji*: 
- 名前 (なまえ) - name
- 客様 (きゃくさま) - guest
- 部屋 (へや) - room
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
