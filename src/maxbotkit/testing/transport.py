from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from maxbotkit.client.transport import BaseTransport, TransportResponse


class FakeTransport(BaseTransport):
    """In-memory transport for client tests.

    The transport returns queued responses in order and records every request in
    :attr:`calls`, which makes it suitable for serialization and retry tests.
    """

    def __init__(self, responses: Iterable[TransportResponse | Exception]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    async def request(self, **kwargs: Any) -> TransportResponse:
        """Return the next queued response or raise the queued exception."""
        self.calls.append(kwargs)
        if not self._responses:
            raise AssertionError("FakeTransport has no more queued responses.")
        current = self._responses.pop(0)
        if isinstance(current, Exception):
            raise current
        return current
