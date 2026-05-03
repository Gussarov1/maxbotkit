from __future__ import annotations

from typing import Any

from maxbotkit.exceptions.base import MaxBotError


class APIError(MaxBotError):
    def __init__(self, status_code: int, message: str, payload: Any = None) -> None:
        super().__init__(f"MAX API returned {status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.payload = payload

    @classmethod
    def from_response(cls, status_code: int, payload: Any) -> "APIError":
        if isinstance(payload, dict):
            message = (
                payload.get("message")
                or payload.get("error")
                or payload.get("description")
                or "Unknown API error"
            )
        else:
            message = str(payload) if payload else "Unknown API error"
        return cls(status_code=status_code, message=message, payload=payload)
