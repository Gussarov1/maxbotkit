from __future__ import annotations

import asyncio

import pytest

from maxbotkit import Bot
from maxbotkit.client.transport import BaseTransport, TransportResponse
from maxbotkit.exceptions.api import APIError
from maxbotkit.methods.edit_message import EditMessage


class FakeTransport(BaseTransport):
    def __init__(self, response: TransportResponse) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    async def request(self, **kwargs):  # type: ignore[override]
        self.calls.append(kwargs)
        return self.response


def test_edit_message_validates_payload() -> None:
    with pytest.raises(ValueError):
        EditMessage(message_id="", text="hello")

    with pytest.raises(ValueError):
        EditMessage(message_id="mid.1", text="")

    with pytest.raises(ValueError):
        EditMessage(message_id="mid.1", text="x" * 4001)


def test_bot_edit_message_builds_expected_request() -> None:
    async def run() -> None:
        transport = FakeTransport(
            TransportResponse(
                status_code=200,
                body={"success": True},
                headers={},
            )
        )
        bot = Bot(token="TOKEN", transport=transport, timeout=2.5)

        success = await bot.edit_message(
            message_id="mid.123",
            text="Updated",
            notify=False,
            format="markdown",
        )

        assert success is True
        assert transport.calls == [
            {
                "method": "PUT",
                "base_url": "https://platform-api.max.ru",
                "path": "/messages",
                "params": {
                    "message_id": "mid.123",
                },
                "json_body": {
                    "text": "Updated",
                    "notify": False,
                    "format": "markdown",
                    "link": None,
                },
                "headers": {"Authorization": "TOKEN"},
                "timeout": 2.5,
            }
        ]

    asyncio.run(run())


def test_bot_edit_message_raises_api_error() -> None:
    async def run() -> None:
        transport = FakeTransport(
            TransportResponse(
                status_code=404,
                body={"error": "message not found"},
                headers={},
            )
        )
        bot = Bot(token="TOKEN", transport=transport)

        with pytest.raises(APIError) as exc_info:
            await bot.edit_message(message_id="mid.404", text="Updated")

        assert exc_info.value.status_code == 404
        assert exc_info.value.message == "message not found"

    asyncio.run(run())
