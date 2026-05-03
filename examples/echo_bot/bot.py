"""Minimal polling bot that answers `/start` and echoes all text messages."""

import asyncio
import os

from dotenv import load_dotenv

from maxbotkit import Bot, Dispatcher, Router
from maxbotkit.filters import Command

load_dotenv()

async def main() -> None:
    token = os.environ.get("MAX_TOKEN")
    if not token:
        raise RuntimeError("Set MAX_TOKEN before running this example.")

    bot = Bot(
        token=token,
        verify_ssl=False,
    )
    dp = Dispatcher()
    router = Router()

    @router.message(Command("start"))
    async def start(message) -> None:
        await message.answer("Бот запущен")

    @router.message()
    async def echo(message) -> None:
        if not message.text:
            return
        await message.reply(f"Echo: {message.text}")

    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
