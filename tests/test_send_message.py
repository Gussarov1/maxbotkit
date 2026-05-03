from __future__ import annotations

import asyncio

import pytest

from maxbotkit import Bot
from maxbotkit.client.transport import BaseTransport, TransportResponse
from maxbotkit.exceptions.api import APIError
from maxbotkit.methods.send_message import SendMessage


class FakeTransport(BaseTransport):
    def __init__(self, response: TransportResponse) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    async def request(self, **kwargs):  # type: ignore[override]
        self.calls.append(kwargs)
        return self.response


def test_send_message_validates_recipient_choice() -> None:
    with pytest.raises(ValueError):
        SendMessage(text="hello")

    with pytest.raises(ValueError):
        SendMessage(text="hello", chat_id=1, user_id=2)


def test_send_message_validates_text_length() -> None:
    with pytest.raises(ValueError):
        SendMessage(text="", chat_id=1)

    with pytest.raises(ValueError):
        SendMessage(text="x" * 4001, chat_id=1)


def test_bot_send_message_builds_expected_request() -> None:
    async def run() -> None:
        transport = FakeTransport(
            TransportResponse(
                status_code=200,
                body={
                    "message": {
                        "recipient": {"chat_id": 123},
                        "timestamp": 1710000000,
                        "body": {"text": "Hello"},
                    }
                },
                headers={},
            )
        )
        bot = Bot(token="TOKEN", transport=transport, timeout=3.5)

        message = await bot.send_message(
            chat_id=123,
            text="Hello",
            notify=False,
            disable_link_preview=True,
            format="markdown",
        )

        assert message.text == "Hello"
        assert message.recipient.chat_id == 123
        assert message._bot is bot
        assert transport.calls == [
            {
                "method": "POST",
                "base_url": "https://platform-api.max.ru",
                "path": "/messages",
                "params": {
                    "chat_id": 123,
                    "user_id": None,
                    "disable_link_preview": True,
                },
                "json_body": {
                    "text": "Hello",
                    "notify": False,
                    "format": "markdown",
                    "link": None,
                },
                "headers": {"Authorization": "TOKEN"},
                "timeout": 3.5,
            }
        ]

    asyncio.run(run())


def test_bot_send_message_raises_api_error() -> None:
    async def run() -> None:
        transport = FakeTransport(
            TransportResponse(
                status_code=429,
                body={"error": "rate limit exceeded"},
                headers={},
            )
        )
        bot = Bot(token="TOKEN", transport=transport)

        with pytest.raises(APIError) as exc_info:
            await bot.send_message(chat_id=123, text="Hello")

        assert exc_info.value.status_code == 429
        assert exc_info.value.message == "rate limit exceeded"

    asyncio.run(run())


def test_bot_passes_ssl_settings_to_default_transport() -> None:
    bot = Bot(token="TOKEN", verify_ssl=False, ca_file="/tmp/company-ca.pem")

    assert bot.transport.verify_ssl is False
    assert bot.transport.ca_file == "/tmp/company-ca.pem"
