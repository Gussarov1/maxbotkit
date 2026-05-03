from __future__ import annotations

import asyncio

import pytest

from maxbotkit import Bot
from maxbotkit.client.transport import BaseTransport, TransportResponse
from maxbotkit.exceptions.api import APIError
from maxbotkit.methods.get_updates import GetUpdates


class FakeTransport(BaseTransport):
    def __init__(self, response: TransportResponse) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    async def request(self, **kwargs):  # type: ignore[override]
        self.calls.append(kwargs)
        return self.response


def test_get_updates_validates_limit_and_timeout() -> None:
    with pytest.raises(ValueError):
        GetUpdates(limit=0)

    with pytest.raises(ValueError):
        GetUpdates(limit=1001)

    with pytest.raises(ValueError):
        GetUpdates(timeout=-1)

    with pytest.raises(ValueError):
        GetUpdates(timeout=91)


def test_bot_get_updates_builds_expected_request() -> None:
    async def run() -> None:
        transport = FakeTransport(
            TransportResponse(
                status_code=200,
                body={
                    "updates": [
                        {
                            "update_type": "message_created",
                            "timestamp": 1710000001,
                            "user_locale": "ru-RU",
                            "message": {
                                "sender": {
                                    "user_id": 50,
                                    "first_name": "Vadim",
                                    "username": "vadim",
                                },
                                "recipient": {
                                    "chat_id": 123,
                                    "chat_type": "dialog",
                                },
                                "timestamp": 1710000000,
                                "body": {
                                    "mid": "mid.abc",
                                    "seq": 7,
                                    "text": "/start",
                                },
                            },
                        }
                    ],
                    "marker": 777,
                },
                headers={},
            )
        )
        bot = Bot(token="TOKEN", transport=transport, timeout=10.0)

        result = await bot.get_updates(
            limit=100,
            timeout=30,
            marker=555,
            types=["message_created", "message_callback"],
        )

        assert result.marker == 777
        assert len(result.updates) == 1
        assert result.updates[0].update_type == "message_created"
        assert result.updates[0].user_locale == "ru-RU"
        assert result.updates[0].message is not None
        assert result.updates[0].message.text == "/start"
        assert result.updates[0].message.message_id == "mid.abc"
        assert result.updates[0].message._bot is bot
        assert result.updates[0].message.recipient.chat_id == 123
        assert transport.calls == [
            {
                "method": "GET",
                "base_url": "https://platform-api.max.ru",
                "path": "/updates",
                "params": {
                    "limit": 100,
                    "timeout": 30,
                    "marker": 555,
                    "types": "message_created,message_callback",
                },
                "json_body": None,
                "headers": {"Authorization": "TOKEN"},
                "timeout": 35.0,
            }
        ]

    asyncio.run(run())


def test_bot_get_updates_raises_api_error() -> None:
    async def run() -> None:
        transport = FakeTransport(
            TransportResponse(
                status_code=429,
                body={"error": "too many requests"},
                headers={},
            )
        )
        bot = Bot(token="TOKEN", transport=transport)

        with pytest.raises(APIError) as exc_info:
            await bot.get_updates()

        assert exc_info.value.status_code == 429
        assert exc_info.value.message == "too many requests"

    asyncio.run(run())
