from __future__ import annotations

from dataclasses import dataclass

from maxbotkit.methods.base import APIMethod


@dataclass(slots=True)
class DeleteMessage(APIMethod):
    """DELETE ``/messages`` request."""

    message_id: str

    http_method: str = "DELETE"
    path: str = "/messages"
    safe_to_retry: bool = False

    def __post_init__(self) -> None:
        if not self.message_id:
            raise ValueError("message_id must be a non-empty string.")

    def build_params(self) -> dict[str, str]:
        """Return query parameters expected by the delete endpoint."""
        return {
            "message_id": self.message_id,
        }
