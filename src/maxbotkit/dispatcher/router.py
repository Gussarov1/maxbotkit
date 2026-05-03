from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from maxbotkit.types.message import Message

MessageHandler = Callable[[Message], object | Awaitable[object]]
MessageFilter = Callable[[Message], bool | Awaitable[bool]]


@dataclass(slots=True)
class MessageObserver:
    """Internal message handler registration with its filter chain."""

    handler: MessageHandler
    filters: tuple[MessageFilter, ...] = ()

    async def matches(self, message: Message) -> bool:
        """Return ``True`` when all filters accept the message."""
        for message_filter in self.filters:
            result = message_filter(message)
            if inspect.isawaitable(result):
                result = await result
            if not result:
                return False
        return True


@dataclass(slots=True)
class Router:
    """Groups message handlers before attaching them to a dispatcher.

    Routers make it easy to organize handlers by feature, module, or domain and
    then include them into a single :class:`Dispatcher`.
    """

    _message_handlers: list[MessageObserver] = field(default_factory=list)

    def message(self, *filters: MessageFilter) -> Callable[[MessageHandler], MessageHandler]:
        """Register a message handler with optional message filters."""
        def decorator(handler: MessageHandler) -> MessageHandler:
            self._message_handlers.append(MessageObserver(handler=handler, filters=filters))
            return handler

        return decorator

    @property
    def message_handlers(self) -> list[MessageObserver]:
        """Return a copy of the registered message handlers."""
        return list(self._message_handlers)
