from __future__ import annotations

import asyncio

from maxbotkit.runtime.polling import PollingRunner, run_polling
from maxbotkit.types.update import UpdateList


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


def make_update(text: str, chat_id: int, *, timestamp: int = 1710000000):
    return {
        "update_type": "message_created",
        "timestamp": timestamp,
        "message": {
            "sender": {
                "user_id": 42,
                "first_name": "Vadim",
            },
            "recipient": {
                "chat_id": chat_id,
                "chat_type": "dialog",
            },
            "timestamp": timestamp,
            "body": {
                "text": text,
            },
        },
    }


def test_polling_runner_processes_updates_and_advances_marker() -> None:
    async def run() -> None:
        bot = FakeBot(
            [
                UpdateList.from_dict(
                    {
                        "updates": [
                            make_update("hello", 100, timestamp=1),
                            make_update("world", 100, timestamp=2),
                        ],
                        "marker": 200,
                    }
                )
            ]
        )
        handled: list[str] = []

        async def on_update(update) -> None:
            handled.append(update.message.text)
            if len(handled) == 2:
                runner.stop()

        runner = PollingRunner(
            bot=bot,
            on_update=on_update,
            limit=50,
            timeout=20,
            types=["message_created"],
        )

        await runner.run()

        assert handled == ["hello", "world"]
        assert runner.marker == 200
        assert bot.calls == [
            {
                "limit": 50,
                "timeout": 20,
                "marker": None,
                "types": ["message_created"],
            }
        ]

    asyncio.run(run())


def test_run_polling_accepts_sync_handler() -> None:
    async def run() -> None:
        bot = FakeBot(
            [
                UpdateList.from_dict(
                    {
                        "updates": [make_update("sync", 101, timestamp=3)],
                        "marker": 300,
                    }
                )
            ]
        )
        seen: list[str] = []
        stop_event = asyncio.Event()

        def on_update(update) -> None:
            seen.append(update.message.text)
            stop_event.set()

        await run_polling(
            bot,
            on_update=on_update,
            timeout=10,
            stop_event=stop_event,
        )

        assert seen == ["sync"]
        assert bot.calls == [
            {
                "limit": 100,
                "timeout": 10,
                "marker": None,
                "types": None,
            }
        ]

    asyncio.run(run())
