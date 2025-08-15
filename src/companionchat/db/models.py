from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Message:
    role: str
    content: str


@dataclass
class Conversation:
    id: UUID
    system_prompt: str
    user_id: str
    created_at: datetime
