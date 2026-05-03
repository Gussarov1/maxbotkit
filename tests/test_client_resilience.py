from __future__ import annotations

import asyncio

import pytest

from maxbotkit import Bot, RetryConfig, TimeoutConfig
from maxbotkit.client.transport import BaseTransport, TransportResponse
from maxbotkit.exceptions.api import RateLimitError, UnauthorizedError
from maxbotkit.exceptions.transport import RetryableTransportError


class SequenceTransport(BaseTransport):
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls: list[dict[str, object]] = []

    async def request(self, **kwargs):  # type: ignore[override]
        self.calls.append(kwargs)
        current = self.responses.pop(0)
        if isinstance(current, Exception):
            raise current
        return current


def test_get_me_retries_retryable_transport_errors() -> None:
    async def run() -> None:
        transport = SequenceTransport(
            [
                RetryableTransportError("temporary outage"),
                TransportResponse(
                    status_code=200,
                    body={"user_id": 1, "first_name": "Bot", "is_bot": True},
                    headers={},
                ),
            ]
        )
        bot = Bot(
            token="TOKEN",
            transport=transport,
            retry_config=RetryConfig(attempts=2, backoff_base=0, backoff_max=0),
        )

        me = await bot.get_me()

        assert me.user_id == 1
        assert len(transport.calls) == 2

    asyncio.run(run())


def test_send_message_does_not_retry_non_safe_method() -> None:
    async def run() -> None:
        transport = SequenceTransport([RetryableTransportError("temporary outage")])
        bot = Bot(
            token="TOKEN",
            transport=transport,
            retry_config=RetryConfig(attempts=3, backoff_base=0, backoff_max=0),
        )

        with pytest.raises(RetryableTransportError):
            await bot.send_message(chat_id=123, text="hello")

        assert len(transport.calls) == 1

    asyncio.run(run())


def test_get_me_retries_rate_limit_then_succeeds() -> None:
    async def run() -> None:
        transport = SequenceTransport(
            [
                TransportResponse(
                    status_code=429,
                    body={"error": "rate limit"},
                    headers={},
                ),
                TransportResponse(
                    status_code=200,
                    body={"user_id": 10, "first_name": "Bot", "is_bot": True},
                    headers={},
                ),
            ]
        )
        bot = Bot(
            token="TOKEN",
            transport=transport,
            retry_config=RetryConfig(attempts=2, backoff_base=0, backoff_max=0),
        )

        me = await bot.get_me()

        assert me.user_id == 10
        assert len(transport.calls) == 2

    asyncio.run(run())


def test_get_me_classifies_unauthorized_error() -> None:
    async def run() -> None:
        transport = SequenceTransport(
            [
                TransportResponse(
                    status_code=401,
                    body={"error": "unauthorized"},
                    headers={},
                )
            ]
        )
        bot = Bot(token="TOKEN", transport=transport)

        with pytest.raises(UnauthorizedError):
            await bot.get_me()

    asyncio.run(run())


def test_bot_accepts_timeout_config() -> None:
    bot = Bot(
        token="TOKEN",
        timeout_config=TimeoutConfig(request_timeout=15.0),
    )

    assert bot.timeout_config.request_timeout == 15.0


def test_bot_retries_server_error_for_safe_method() -> None:
    async def run() -> None:
        transport = SequenceTransport(
            [
                TransportResponse(status_code=503, body={"error": "unavailable"}, headers={}),
                TransportResponse(
                    status_code=200,
                    body={"user_id": 50, "first_name": "Bot", "is_bot": True},
                    headers={},
                ),
            ]
        )
        bot = Bot(
            token="TOKEN",
            transport=transport,
            retry_config=RetryConfig(attempts=2, backoff_base=0, backoff_max=0),
        )

        me = await bot.get_me()

        assert me.user_id == 50
        assert len(transport.calls) == 2

    asyncio.run(run())


def test_get_me_raises_rate_limit_after_retry_budget() -> None:
    async def run() -> None:
        transport = SequenceTransport(
            [
                TransportResponse(status_code=429, body={"error": "limit"}, headers={}),
                TransportResponse(status_code=429, body={"error": "limit"}, headers={}),
            ]
        )
        bot = Bot(
            token="TOKEN",
            transport=transport,
            retry_config=RetryConfig(attempts=2, backoff_base=0, backoff_max=0),
        )

        with pytest.raises(RateLimitError):
            await bot.get_me()

    asyncio.run(run())
