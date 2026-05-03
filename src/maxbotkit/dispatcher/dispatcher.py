from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from maxbotkit._internal.typing import BotLike
from maxbotkit.dispatcher.router import MessageFilter, MessageObserver, Router
from maxbotkit.runtime.polling import run_polling
from maxbotkit.types.message import Message
from maxbotkit.types.update import Update

MessageHandler = Callable[[Message], object | Awaitable[object]]


@dataclass(slots=True)
class Dispatcher:
    _message_handlers: list[MessageObserver] = field(default_factory=list)

    def message(self, *filters: MessageFilter) -> Callable[[MessageHandler], MessageHandler]:
        def decorator(handler: MessageHandler) -> MessageHandler:
            self._message_handlers.append(MessageObserver(handler=handler, filters=filters))
            return handler

        return decorator

    def include_router(self, router: Router) -> None:
        self._message_handlers.extend(router.message_handlers)

    async def feed_update(self, update: Update) -> None:
        if update.update_type != "message_created":
            return
        if update.message is None:
            return

        for observer in self._message_handlers:
            if not await observer.matches(update.message):
                continue

            result = observer.handler(update.message)
            if inspect.isawaitable(result):
                await result

    async def start_polling(
        self,
        bot: BotLike,
        *,
        limit: int = 100,
        timeout: int = 30,
        marker: int | None = None,
        types: list[str] | None = None,
        stop_event: asyncio.Event | None = None,
    ) -> None:
        allowed_types = types or ["message_created"]
        await run_polling(
            bot,
            on_update=self.feed_update,
            limit=limit,
            timeout=timeout,
            marker=marker,
            types=allowed_types,
            stop_event=stop_event,
        )
