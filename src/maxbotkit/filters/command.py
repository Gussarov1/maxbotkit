from __future__ import annotations

from dataclasses import dataclass

from maxbotkit.types.message import Message


@dataclass(slots=True)
class Command:
    """Match text messages that start with a concrete slash command.

    Examples:
        `Command("start")` matches `/start` and `/start@my_bot`.
    """

    name: str

    async def __call__(self, message: Message) -> bool:
        """Return ``True`` when the message text matches the configured command."""
        text = message.text
        if not text:
            return False

        command, _, _rest = text.partition(" ")
        if not command.startswith("/"):
            return False

        command_name = command[1:].split("@", 1)[0]
        return command_name == self.name
