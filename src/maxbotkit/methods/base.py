from __future__ import annotations

from typing import Any


class APIMethod:
    """Base description of a single MAX API request."""

    http_method: str
    path: str
    safe_to_retry: bool = False

    def build_params(self) -> dict[str, Any]:
        """Return query parameters for the request."""
        return {}

    def build_body(self) -> dict[str, Any]:
        """Return a JSON body for the request."""
        return {}

    def request_timeout(self, default_timeout: float) -> float:
        """Return the effective timeout for this method."""
        return default_timeout
