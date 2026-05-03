from __future__ import annotations

import asyncio

from maxbotkit import Command, Dispatcher, Router
from maxbotkit.types.update import Update


def make_message_update(text: str | None, *, timestamp: int = 1710000000) -> Update:
    payload: dict[str, object] = {
        "update_type": "message_created",
        "timestamp": timestamp,
        "message": {
            "sender": {
                "user_id": 42,
                "first_name": "Vadim",
            },
            "recipient": {
                "chat_id": 100,
                "chat_type": "dialog",
            },
            "timestamp": timestamp,
            "body": {
                "text": text,
            },
        },
    }
    return Update.from_dict(payload)


def test_command_matches_supported_command_forms() -> None:
    async def run() -> None:
        command = Command("start")

        assert await command(make_message_update("/start").message) is True
        assert await command(make_message_update("/start hello").message) is True
        assert await command(make_message_update("/start@mybot").message) is True
        assert await command(make_message_update("/help").message) is False
        assert await command(make_message_update("start").message) is False
        assert await command(make_message_update(None).message) is False

    asyncio.run(run())


def test_dispatcher_message_filter_limits_handler_execution() -> None:
    async def run() -> None:
        dp = Dispatcher()
        seen: list[str] = []

        @dp.message(Command("start"))
        async def start(message) -> None:
            seen.append(message.text)

        await dp.feed_update(make_message_update("/help"))
        await dp.feed_update(make_message_update("/start"))

        assert seen == ["/start"]

    asyncio.run(run())


def test_router_filter_is_respected_after_include_router() -> None:
    async def run() -> None:
        dp = Dispatcher()
        router = Router()
        seen: list[str] = []

        @router.message(Command("ping"))
        async def ping(message) -> None:
            seen.append(message.text)

        dp.include_router(router)

        await dp.feed_update(make_message_update("/pong"))
        await dp.feed_update(make_message_update("/ping now"))

        assert seen == ["/ping now"]

    asyncio.run(run())
