from __future__ import annotations

import asyncio

from maxbotkit import Dispatcher, Router
from maxbotkit.types.update import Update


def make_message_update(text: str, *, timestamp: int = 1710000000) -> Update:
    return Update.from_dict(
        {
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
    )


def test_router_registers_message_handlers() -> None:
    router = Router()

    @router.message()
    async def echo(message) -> None:
        return None

    assert len(router.message_handlers) == 1
    assert router.message_handlers[0].handler is echo
    assert router.message_handlers[0].filters == ()


def test_dispatcher_include_router_routes_messages() -> None:
    async def run() -> None:
        dp = Dispatcher()
        router = Router()
        seen: list[str] = []

        @router.message()
        async def echo(message) -> None:
            seen.append(message.text)

        dp.include_router(router)

        await dp.feed_update(make_message_update("hello from router"))

        assert seen == ["hello from router"]

    asyncio.run(run())
