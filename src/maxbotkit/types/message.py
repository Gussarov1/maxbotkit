from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from maxbotkit.types.base import BaseModel
from maxbotkit.types.user import User


@dataclass(slots=True)
class Recipient(BaseModel):
    chat_id: int | None = None
    user_id: int | None = None
    chat_type: str | None = None


@dataclass(slots=True)
class MessageBody(BaseModel):
    mid: str | None = None
    seq: int | None = None
    text: str | None = None


@dataclass(slots=True)
class Message(BaseModel):
    sender: User | None
    recipient: Recipient
    timestamp: int
    body: MessageBody | None = None
    url: str | None = None
    _bot: Any = field(default=None, repr=False, compare=False)

    @property
    def text(self) -> str | None:
        if self.body is None:
            return None
        return self.body.text

    @property
    def message_id(self) -> str | None:
        if self.body is None:
            return None
        return self.body.mid

    async def answer(
        self,
        text: str,
        *,
        notify: bool = True,
        disable_link_preview: bool | None = None,
        format: str | None = None,
        link: dict[str, str] | None = None,
    ) -> "Message":
        if self._bot is None:
            raise RuntimeError("Message is not bound to a bot.")
        if self.recipient.chat_id is not None:
            return await self._bot.send_message(
                chat_id=self.recipient.chat_id,
                text=text,
                notify=notify,
                disable_link_preview=disable_link_preview,
                format=format,
                link=link,
            )
        if self.recipient.user_id is not None:
            return await self._bot.send_message(
                user_id=self.recipient.user_id,
                text=text,
                notify=notify,
                disable_link_preview=disable_link_preview,
                format=format,
                link=link,
            )
        raise RuntimeError("Message recipient does not contain chat_id or user_id.")

    async def reply(
        self,
        text: str,
        *,
        notify: bool = True,
        disable_link_preview: bool | None = None,
        format: str | None = None,
    ) -> "Message":
        if self.message_id is None:
            raise RuntimeError("Message does not contain a message_id.")
        return await self.answer(
            text,
            notify=notify,
            disable_link_preview=disable_link_preview,
            format=format,
            link={"type": "reply", "mid": self.message_id},
        )

    @classmethod
    def from_api_response(cls, data: dict[str, Any], *, bot: Any = None) -> "Message":
        payload = data.get("message", data)
        sender_payload = payload.get("sender")
        body_payload = payload.get("body")
        return cls(
            sender=User.from_dict(sender_payload) if isinstance(sender_payload, dict) else None,
            recipient=Recipient.from_dict(payload["recipient"]),
            timestamp=payload["timestamp"],
            body=MessageBody.from_dict(body_payload) if isinstance(body_payload, dict) else None,
            url=payload.get("url"),
            _bot=bot,
        )
