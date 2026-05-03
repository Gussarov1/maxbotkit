from __future__ import annotations

import asyncio

import pytest

from maxbotkit.client.transport import TransportResponse
from maxbotkit.testing import FakeTransport


def test_fake_transport_returns_queued_response() -> None:
    async def run() -> None:
        transport = FakeTransport(
            [
                TransportResponse(status_code=200, body={"ok": True}, headers={}),
            ]
        )

        response = await transport.request(method="GET", base_url="https://example.com", path="/ping")

        assert response.status_code == 200
        assert response.body == {"ok": True}
        assert transport.calls == [
            {"method": "GET", "base_url": "https://example.com", "path": "/ping"}
        ]

    asyncio.run(run())


def test_fake_transport_raises_queued_exception() -> None:
    async def run() -> None:
        transport = FakeTransport([RuntimeError("boom")])

        with pytest.raises(RuntimeError, match="boom"):
            await transport.request(method="GET", base_url="https://example.com", path="/ping")

    asyncio.run(run())
