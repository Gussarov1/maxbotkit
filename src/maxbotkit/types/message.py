from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from maxbotkit._internal.typing import BotLike
from maxbotkit.types.base import BaseModel
from maxbotkit.types.user import User


@dataclass(slots=True)
class Recipient(BaseModel):
    """Target information for a MAX message."""

    chat_id: int | None = None
    user_id: int | None = None
    chat_type: str | None = None


@dataclass(slots=True)
class MessageBody(BaseModel):
    """Message body payload returned by the MAX API."""

    mid: str | None = None
    seq: int | None = None
    text: str | None = None


@dataclass(slots=True)
class Message(BaseModel):
    """Incoming or outgoing MAX message model.

    When a message is bound to a bot instance, convenience helpers such as
    :meth:`answer` and :meth:`reply` become available.
    """

    sender: User | None
    recipient: Recipient
    timestamp: int
    body: MessageBody | None = None
    url: str | None = None
    _bot: BotLike | None = field(default=None, repr=False, compare=False)

    @property
    def text(self) -> str | None:
        """Return the text body of the message when available."""
        if self.body is None:
            return None
        return self.body.text

    @property
    def message_id(self) -> str | None:
        """Return the MAX message identifier (`mid`) when available."""
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
    ) -> Message:
        """Send a new message to the same chat or user as this message.

        This helper is the ergonomic equivalent of calling
        :meth:`maxbotkit.client.bot.Bot.send_message` with the current
        recipient already filled in.
        """
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
    ) -> Message:
        """Send a linked reply to this exact message."""
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
    def from_api_response(cls, data: dict[str, Any], *, bot: BotLike | None = None) -> Message:
        """Build a :class:`Message` from a raw MAX API payload."""
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
