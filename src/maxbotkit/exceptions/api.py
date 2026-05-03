from __future__ import annotations

from typing import Any

from maxbotkit.exceptions.base import MaxBotKitError


class APIError(MaxBotKitError):
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
        error_cls = _error_class_for_status(status_code)
        return error_cls(status_code=status_code, message=message, payload=payload)


class BadRequestError(APIError):
    pass


class UnauthorizedError(APIError):
    pass


class ForbiddenError(APIError):
    pass


class NotFoundError(APIError):
    pass


class RateLimitError(APIError):
    pass


class ServerError(APIError):
    pass


def _error_class_for_status(status_code: int) -> type[APIError]:
    if status_code == 400:
        return BadRequestError
    if status_code == 401:
        return UnauthorizedError
    if status_code == 403:
        return ForbiddenError
    if status_code == 404:
        return NotFoundError
    if status_code == 429:
        return RateLimitError
    if status_code >= 500:
        return ServerError
    return APIError
