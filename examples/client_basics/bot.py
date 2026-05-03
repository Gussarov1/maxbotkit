import asyncio
import os

from dotenv import load_dotenv

from maxbotkit import Bot, RetryConfig, TimeoutConfig

load_dotenv()


async def main() -> None:
    bot = Bot(
        token=os.environ["MAX_TOKEN"],
        verify_ssl=False,
        timeout_config=TimeoutConfig(request_timeout=15.0),
        retry_config=RetryConfig(
            attempts=3,
            backoff_base=0.5,
            backoff_max=3.0,
            jitter=True,
        ),
    )

    me = await bot.get_me()
    print("bot:", me.user_id, me.first_name, me.username)

    chats = await bot.get_chats(count=20)
    for chat in chats.chats:
        print("chat:", chat.chat_id, chat.title, chat.type)


if __name__ == "__main__":
    asyncio.run(main())
