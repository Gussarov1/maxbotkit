from __future__ import annotations

import asyncio

import pytest

from maxbotkit import Bot
from maxbotkit.client.transport import BaseTransport, TransportResponse
from maxbotkit.exceptions.api import APIError
from maxbotkit.methods.delete_message import DeleteMessage


class FakeTransport(BaseTransport):
    def __init__(self, response: TransportResponse) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    async def request(self, **kwargs):  # type: ignore[override]
        self.calls.append(kwargs)
        return self.response


def test_delete_message_validates_message_id() -> None:
    with pytest.raises(ValueError):
        DeleteMessage(message_id="")


def test_bot_delete_message_builds_expected_request() -> None:
    async def run() -> None:
        transport = FakeTransport(
            TransportResponse(
                status_code=200,
                body={"success": True},
                headers={},
            )
        )
        bot = Bot(token="TOKEN", transport=transport, timeout=2.5)

        success = await bot.delete_message(message_id="mid.delete")

        assert success is True
        assert transport.calls == [
            {
                "method": "DELETE",
                "base_url": "https://platform-api.max.ru",
                "path": "/messages",
                "params": {
                    "message_id": "mid.delete",
                },
                "json_body": None,
                "headers": {"Authorization": "TOKEN"},
                "timeout": 2.5,
            }
        ]

    asyncio.run(run())


def test_bot_delete_message_raises_api_error() -> None:
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
            await bot.delete_message(message_id="mid.forbidden")

        assert exc_info.value.status_code == 403
        assert exc_info.value.message == "forbidden"

    asyncio.run(run())
