from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from maxbotkit.types.base import BaseModel


@dataclass(slots=True)
class Chat(BaseModel):
    chat_id: int | None = None
    type: str | None = None
    status: str | None = None
    title: str | None = None
    last_event_time: int | None = None
    participants_count: int | None = None
    is_public: bool | None = None
    description: str | None = None


@dataclass(slots=True)
class ChatList(BaseModel):
    chats: list[Chat]
    marker: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChatList":
        chats_payload = data.get("chats", [])
        chats = [Chat.from_dict(item) for item in chats_payload if isinstance(item, dict)]
        return cls(
            chats=chats,
            marker=data.get("marker"),
        )
