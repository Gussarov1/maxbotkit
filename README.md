# maxbotkit

Async Python framework for MAX bots with aiogram-like DX and production-oriented building blocks.

`maxbotkit` is an early pre-alpha package focused on giving MAX bot developers a clean async client, polling runtime, routing primitives, and a testable codebase that can grow into a production-grade framework.

## Current capabilities

- Async `Bot` client
- `send_message`, `get_me`, `get_chats`, `get_updates`, `get_subscriptions`
- Long polling runtime
- `Dispatcher` and `Router`
- `Command` filter
- `message.answer()` and `message.reply()`

## Installation

```bash
python -m pip install maxbotkit
```

For local development:

```bash
python -m pip install -e .[dev] --no-build-isolation
```

## Quickstart

```python
import asyncio
import os

from maxbotkit import Bot, Command, Dispatcher, Router


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
```

## Development

Run tests:

```bash
env PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests
```

Run linting:

```bash
python -m ruff check .
python -m mypy src
```

## Roadmap

`0.0.1` is the bootstrap release. The next milestones focus on:

- stronger client typing
- broader MAX API coverage
- middleware and dependency injection
- richer filters
- observability and reliability layers

## Status

This project is currently pre-alpha and the public API is expected to evolve quickly.
