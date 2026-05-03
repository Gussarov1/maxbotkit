from __future__ import annotations

from dataclasses import dataclass

from maxbotkit.methods.base import APIMethod


@dataclass(slots=True)
class SendMessage(APIMethod):
    """POST ``/messages`` request for sending a text message."""

    text: str
    chat_id: int | None = None
    user_id: int | None = None
    notify: bool = True
    disable_link_preview: bool | None = None
    format: str | None = None
    link: dict[str, str] | None = None

    http_method: str = "POST"
    path: str = "/messages"

    def __post_init__(self) -> None:
        recipients = [self.chat_id is not None, self.user_id is not None]
        if sum(recipients) != 1:
            raise ValueError("Exactly one of chat_id or user_id must be provided.")
        if not self.text:
            raise ValueError("text must be a non-empty string when attachments are not used.")
        if len(self.text) > 4000:
            raise ValueError("text must be at most 4000 characters long.")
        if self.format not in {None, "markdown", "html"}:
            raise ValueError("format must be one of: 'markdown', 'html', or None.")

    def build_params(self) -> dict[str, int | bool | None]:
        """Return query parameters expected by the send endpoint."""
        return {
            "chat_id": self.chat_id,
            "user_id": self.user_id,
            "disable_link_preview": self.disable_link_preview,
        }

    def build_body(self) -> dict[str, str | bool | dict[str, str] | None]:
        """Return the JSON body for the send request."""
        return {
            "text": self.text,
            "notify": self.notify,
            "format": self.format,
            "link": self.link,
        }
