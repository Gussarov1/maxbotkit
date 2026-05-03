import asyncio
import os

from dotenv import load_dotenv

from maxbotkit import Bot, Dispatcher, Router
from maxbotkit.filters import Command

load_dotenv()

bot = Bot(
    token=os.environ["MAX_TOKEN"],
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


async def main() -> None:
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
