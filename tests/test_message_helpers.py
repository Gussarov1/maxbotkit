from __future__ import annotations

import asyncio

from maxbotkit.types.message import Message


class FakeBot:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def send_message(self, **kwargs):
        self.calls.append(kwargs)
        return {"ok": True}


def test_message_exposes_message_id() -> None:
    message = Message.from_api_response(
        {
            "recipient": {
                "chat_id": 100,
                "chat_type": "chat",
            },
            "timestamp": 1710000000,
            "body": {
                "mid": "mid.ffff",
                "seq": 1,
                "text": "hello",
            },
        }
    )

    assert message.message_id == "mid.ffff"


def test_message_answer_sends_to_same_chat() -> None:
    async def run() -> None:
        bot = FakeBot()
        message = Message.from_api_response(
            {
                "recipient": {
                    "chat_id": 555,
                    "chat_type": "chat",
                },
                "timestamp": 1710000000,
                "body": {
                    "mid": "mid.1",
                    "seq": 1,
                    "text": "hello",
                },
            },
            bot=bot,
        )

        await message.answer("pong")

        assert bot.calls == [
            {
                "chat_id": 555,
                "text": "pong",
                "notify": True,
                "disable_link_preview": None,
                "format": None,
                "link": None,
            }
        ]

    asyncio.run(run())


def test_message_reply_sends_reply_link() -> None:
    async def run() -> None:
        bot = FakeBot()
        message = Message.from_api_response(
            {
                "recipient": {
                    "chat_id": 777,
                    "chat_type": "chat",
                },
                "timestamp": 1710000000,
                "body": {
                    "mid": "mid.reply",
                    "seq": 99,
                    "text": "hello",
                },
            },
            bot=bot,
        )

        await message.reply("reply text")

        assert bot.calls == [
            {
                "chat_id": 777,
                "text": "reply text",
                "notify": True,
                "disable_link_preview": None,
                "format": None,
                "link": {
                    "type": "reply",
                    "mid": "mid.reply",
                },
            }
        ]

    asyncio.run(run())
