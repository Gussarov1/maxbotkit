from __future__ import annotations

import asyncio

import pytest

from maxbotkit import Bot
from maxbotkit.client.transport import BaseTransport, TransportResponse
from maxbotkit.exceptions.api import APIError
from maxbotkit.methods.get_chats import GetChats


class FakeTransport(BaseTransport):
    def __init__(self, response: TransportResponse) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    async def request(self, **kwargs):  # type: ignore[override]
        self.calls.append(kwargs)
        return self.response


def test_get_chats_validates_count_range() -> None:
    with pytest.raises(ValueError):
        GetChats(count=0)

    with pytest.raises(ValueError):
        GetChats(count=101)


def test_bot_get_chats_builds_expected_request() -> None:
    async def run() -> None:
        transport = FakeTransport(
            TransportResponse(
                status_code=200,
                body={
                    "chats": [
                        {
                            "chat_id": 101,
                            "type": "chat",
                            "status": "active",
                            "title": "Payments",
                            "last_event_time": 1710000000,
                            "participants_count": 5,
                            "is_public": False,
                            "description": "Treasury room",
                        }
                    ],
                    "marker": 999,
                },
                headers={},
            )
        )
        bot = Bot(token="TOKEN", transport=transport, timeout=2.0)

        result = await bot.get_chats(count=10, marker=123)

        assert result.marker == 999
        assert len(result.chats) == 1
        assert result.chats[0].chat_id == 101
        assert result.chats[0].title == "Payments"
        assert transport.calls == [
            {
                "method": "GET",
                "base_url": "https://platform-api.max.ru",
                "path": "/chats",
                "params": {
                    "count": 10,
                    "marker": 123,
                },
                "json_body": None,
                "headers": {"Authorization": "TOKEN"},
                "timeout": 2.0,
            }
        ]

    asyncio.run(run())


def test_bot_get_chats_raises_api_error() -> None:
    async def run() -> None:
        transport = FakeTransport(
            TransportResponse(
                status_code=401,
                body={"error": "unauthorized"},
                headers={},
            )
        )
        bot = Bot(token="TOKEN", transport=transport)

        with pytest.raises(APIError) as exc_info:
            await bot.get_chats()

        assert exc_info.value.status_code == 401
        assert exc_info.value.message == "unauthorized"

    asyncio.run(run())
