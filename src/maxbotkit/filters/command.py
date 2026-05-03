from __future__ import annotations

from dataclasses import dataclass

from maxbotkit.types.message import Message


@dataclass(slots=True)
class Command:
    name: str

    async def __call__(self, message: Message) -> bool:
        text = message.text
        if not text:
            return False

        command, _, _rest = text.partition(" ")
        if not command.startswith("/"):
            return False

        command_name = command[1:].split("@", 1)[0]
        return command_name == self.name
