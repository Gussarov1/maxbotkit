from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from maxbotkit.types.update import Update, UpdateList

UpdateHandler = Callable[[Update], object | Awaitable[object]]


@dataclass(slots=True)
class PollingRunner:
    bot: object
    on_update: UpdateHandler
    limit: int = 100
    timeout: int = 30
    marker: int | None = None
    types: list[str] | None = None
    stop_event: asyncio.Event = field(default_factory=asyncio.Event)

    async def run(self) -> None:
        while not self.stop_event.is_set():
            page = await self.bot.get_updates(
                limit=self.limit,
                timeout=self.timeout,
                marker=self.marker,
                types=self.types,
            )
            self.marker = page.marker

            for update in page.updates:
                update._bot = self.bot
                if update.message is not None:
                    update.message._bot = self.bot
                await self._handle_update(update)
                if self.stop_event.is_set():
                    break

    def stop(self) -> None:
        self.stop_event.set()

    async def _handle_update(self, update: Update) -> None:
        result = self.on_update(update)
        if inspect.isawaitable(result):
            await result


async def run_polling(
    bot: object,
    *,
    on_update: UpdateHandler,
    limit: int = 100,
    timeout: int = 30,
    marker: int | None = None,
    types: list[str] | None = None,
    stop_event: asyncio.Event | None = None,
) -> None:
    runner = PollingRunner(
        bot=bot,
        on_update=on_update,
        limit=limit,
        timeout=timeout,
        marker=marker,
        types=types,
        stop_event=stop_event or asyncio.Event(),
    )
    await runner.run()
