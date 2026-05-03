from __future__ import annotations

from dataclasses import dataclass

from maxbotkit.methods.base import APIMethod


@dataclass(slots=True)
class EditMessage(APIMethod):
    message_id: str
    text: str
    notify: bool = True
    format: str | None = None
    link: dict[str, str] | None = None

    http_method: str = "PUT"
    path: str = "/messages"
    safe_to_retry: bool = False

    def __post_init__(self) -> None:
        if not self.message_id:
            raise ValueError("message_id must be a non-empty string.")
        if not self.text:
            raise ValueError("text must be a non-empty string when attachments are not used.")
        if len(self.text) > 4000:
            raise ValueError("text must be at most 4000 characters long.")
        if self.format not in {None, "markdown", "html"}:
            raise ValueError("format must be one of: 'markdown', 'html', or None.")

    def build_params(self) -> dict[str, str]:
        return {
            "message_id": self.message_id,
        }

    def build_body(self) -> dict[str, str | bool | dict[str, str] | None]:
        return {
            "text": self.text,
            "notify": self.notify,
            "format": self.format,
            "link": self.link,
        }
