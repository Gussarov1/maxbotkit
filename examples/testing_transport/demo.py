import asyncio

from maxbotkit import Bot
from maxbotkit.client.transport import TransportResponse
from maxbotkit.testing import FakeTransport


async def main() -> None:
    transport = FakeTransport(
        [
            TransportResponse(
                status_code=200,
                body={"user_id": 1, "first_name": "Bot", "is_bot": True},
                headers={},
            )
        ]
    )

    bot = Bot(token="TOKEN", transport=transport)
    me = await bot.get_me()

    print(me.user_id, me.first_name)
    print(transport.calls)


if __name__ == "__main__":
    asyncio.run(main())
