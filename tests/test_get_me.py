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


def test_bot_get_me_builds_expected_request() -> None:
    async def run() -> None:
        transport = FakeTransport(
            TransportResponse(
                status_code=200,
                body={
                    "user_id": 777,
                    "first_name": "MaxGuard",
                    "username": "max_guard_bot",
                    "is_bot": True,
                    "description": "Internal bot",
                },
                headers={},
            )
        )
        bot = Bot(token="TOKEN", transport=transport, timeout=1.5)

        me = await bot.get_me()

        assert me.user_id == 777
        assert me.first_name == "MaxGuard"
        assert me.username == "max_guard_bot"
        assert me.is_bot is True
        assert transport.calls == [
            {
                "method": "GET",
                "base_url": "https://platform-api.max.ru",
                "path": "/me",
                "params": {},
                "json_body": None,
                "headers": {"Authorization": "TOKEN"},
                "timeout": 1.5,
            }
        ]

    asyncio.run(run())


def test_bot_get_me_raises_api_error() -> None:
    async def run() -> None:
        transport = FakeTransport(
            TransportResponse(
                status_code=403,
                body={"error": "forbidden"},
                headers={},
            )
        )
        bot = Bot(token="TOKEN", transport=transport)

        with pytest.raises(APIError) as exc_info:
            await bot.get_me()

        assert exc_info.value.status_code == 403
        assert exc_info.value.message == "forbidden"

    asyncio.run(run())
