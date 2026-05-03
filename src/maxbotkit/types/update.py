from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from maxbotkit._internal.typing import BotLike
from maxbotkit.types.base import BaseModel
from maxbotkit.types.message import Message


@dataclass(slots=True)
class Update(BaseModel):
    """Single MAX update entry returned by ``get_updates``."""

    update_type: str
    timestamp: int
    message: Message | None = None
    user_locale: str | None = None
    payload: dict[str, Any] | None = None
    _bot: BotLike | None = field(default=None, repr=False, compare=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, bot: BotLike | None = None) -> "Update":
        """Build an update model from a raw API payload."""
        message_payload = data.get("message")
        message = None
        if isinstance(message_payload, dict):
            message = Message.from_api_response(message_payload, bot=bot)

        return cls(
            update_type=data["update_type"],
            timestamp=data["timestamp"],
            message=message,
            user_locale=data.get("user_locale"),
            payload=data,
            _bot=bot,
        )


@dataclass(slots=True)
class UpdateList(BaseModel):
    """Paginated collection of updates returned by long polling."""

    updates: list[Update]
    marker: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], *, bot: BotLike | None = None) -> "UpdateList":
        """Build an update page from a raw API payload."""
        updates_payload = data.get("updates", [])
        updates = [
            Update.from_dict(item, bot=bot)
            for item in updates_payload
            if isinstance(item, dict)
        ]
        return cls(
            updates=updates,
            marker=data.get("marker"),
        )
