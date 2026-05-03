from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from maxbotkit.types.message import Message

MessageHandler = Callable[[Message], object | Awaitable[object]]
MessageFilter = Callable[[Message], bool | Awaitable[bool]]


@dataclass(slots=True)
class MessageObserver:
    handler: MessageHandler
    filters: tuple[MessageFilter, ...] = ()

    async def matches(self, message: Message) -> bool:
        for message_filter in self.filters:
            result = message_filter(message)
            if inspect.isawaitable(result):
                result = await result
            if not result:
                return False
        return True


@dataclass(slots=True)
class Router:
    _message_handlers: list[MessageObserver] = field(default_factory=list)

    def message(self, *filters: MessageFilter) -> Callable[[MessageHandler], MessageHandler]:
        def decorator(handler: MessageHandler) -> MessageHandler:
            self._message_handlers.append(MessageObserver(handler=handler, filters=filters))
            return handler

        return decorator

    @property
    def message_handlers(self) -> list[MessageObserver]:
        return list(self._message_handlers)
