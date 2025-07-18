from dataclasses import dataclass
from uuid import UUID


@dataclass
class Message:
    role: str
    content: str


@dataclass
class Conversation:
    id: UUID
    messages: list[Message]
