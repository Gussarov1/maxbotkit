from __future__ import annotations

from typing import Any

from maxbotkit.exceptions.base import MaxBotKitError


class APIError(MaxBotKitError):
    """Base class for errors returned by the MAX HTTP API."""

    def __init__(self, status_code: int, message: str, payload: Any = None) -> None:
        super().__init__(f"MAX API returned {status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.payload = payload

    @classmethod
    def from_response(cls, status_code: int, payload: Any) -> "APIError":
        """Build the most specific API error for a response payload."""
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
    """Raised for ``400 Bad Request`` responses."""


class UnauthorizedError(APIError):
    """Raised for ``401 Unauthorized`` responses."""


class ForbiddenError(APIError):
    """Raised for ``403 Forbidden`` responses."""


class NotFoundError(APIError):
    """Raised for ``404 Not Found`` responses."""


class RateLimitError(APIError):
    """Raised for ``429 Too Many Requests`` responses."""


class ServerError(APIError):
    """Raised for ``5xx`` server-side MAX API responses."""


def _error_class_for_status(status_code: int) -> type[APIError]:
    """Return the exception type that best matches an HTTP status code."""
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
