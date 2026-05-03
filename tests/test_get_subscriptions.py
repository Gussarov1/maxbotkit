from __future__ import annotations

import asyncio

import pytest

from maxbotkit import Bot
from maxbotkit.client.transport import BaseTransport, TransportResponse
from maxbotkit.exceptions.api import APIError


class FakeTransport(BaseTransport):
    def __init__(self, response: TransportResponse) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    async def request(self, **kwargs):  # type: ignore[override]
        self.calls.append(kwargs)
        return self.response


def test_bot_get_subscriptions_builds_expected_request() -> None:
    async def run() -> None:
        transport = FakeTransport(
            TransportResponse(
                status_code=200,
                body={
                    "subscriptions": [
                        {
                            "url": "https://example.internal/max/webhook",
                            "time": 1710000000,
                            "update_types": ["message_created", "message_callback"],
                            "version": "v1",
                            "secret_key": "masked",
                        }
                    ]
                },
                headers={},
            )
        )
        bot = Bot(token="TOKEN", transport=transport, timeout=4.0)

        result = await bot.get_subscriptions()

        assert len(result.subscriptions) == 1
        assert result.subscriptions[0].url == "https://example.internal/max/webhook"
        assert result.subscriptions[0].update_types == ["message_created", "message_callback"]
        assert transport.calls == [
            {
                "method": "GET",
                "base_url": "https://platform-api.max.ru",
                "path": "/subscriptions",
                "params": {},
                "json_body": None,
                "headers": {"Authorization": "TOKEN"},
                "timeout": 4.0,
            }
        ]

    asyncio.run(run())


def test_bot_get_subscriptions_raises_api_error() -> None:
    async def run() -> None:
        transport = FakeTransport(
            TransportResponse(
                status_code=503,
                body={"error": "service unavailable"},
                headers={},
            )
        )
        bot = Bot(token="TOKEN", transport=transport)

        with pytest.raises(APIError) as exc_info:
            await bot.get_subscriptions()

        assert exc_info.value.status_code == 503
        assert exc_info.value.message == "service unavailable"

    asyncio.run(run())
