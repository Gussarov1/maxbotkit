from __future__ import annotations

import asyncio

from maxbotkit import Dispatcher
from maxbotkit.types.update import Update, UpdateList


class FakeBot:
    def __init__(self, pages: list[UpdateList]) -> None:
        self.pages = list(pages)
        self.calls: list[dict[str, object]] = []

    async def get_updates(
        self,
        *,
        limit: int | None = None,
        timeout: int | None = None,
        marker: int | None = None,
        types: list[str] | None = None,
    ) -> UpdateList:
        self.calls.append(
            {
                "limit": limit,
                "timeout": timeout,
                "marker": marker,
                "types": types,
            }
        )
        if self.pages:
            return self.pages.pop(0)
        return UpdateList(updates=[], marker=marker)


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


def test_dispatcher_calls_registered_message_handlers() -> None:
    async def run() -> None:
        dp = Dispatcher()
        seen: list[str] = []

        @dp.message()
        async def echo(message) -> None:
            seen.append(message.text)

        await dp.feed_update(make_message_update("hello"))

        assert seen == ["hello"]

    asyncio.run(run())


def test_dispatcher_start_polling_routes_message_updates() -> None:
    async def run() -> None:
        dp = Dispatcher()
        handled: list[str] = []
        stop_event = asyncio.Event()

        @dp.message()
        async def echo(message) -> None:
            handled.append(message.text)
            stop_event.set()

        bot = FakeBot(
            [
                UpdateList(
                    updates=[make_message_update("first")],
                    marker=321,
                )
            ]
        )

        polling_task = asyncio.create_task(
            dp.start_polling(
                bot,
                timeout=10,
                types=["message_created"],
                stop_event=stop_event,
            )
        )
        await asyncio.wait_for(stop_event.wait(), timeout=1)
        await asyncio.wait_for(polling_task, timeout=1)

        assert handled == ["first"]
        assert bot.calls == [
            {
                "limit": 100,
                "timeout": 10,
                "marker": None,
                "types": ["message_created"],
            }
        ]

    asyncio.run(run())


def test_dispatcher_ignores_non_message_updates() -> None:
    async def run() -> None:
        dp = Dispatcher()
        seen: list[str] = []

        @dp.message()
        async def echo(message) -> None:
            seen.append(message.text)

        await dp.feed_update(
            Update.from_dict(
                {
                    "update_type": "bot_started",
                    "timestamp": 1,
                    "chat_id": 100,
                    "payload": "hello",
                }
            )
        )

        assert seen == []

    asyncio.run(run())
