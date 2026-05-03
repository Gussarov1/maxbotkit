# maxbotkit

Async Python framework for MAX bots with aiogram-like DX and production-oriented building blocks.

`maxbotkit` is an early pre-alpha package focused on giving MAX bot developers a clean async client, polling runtime, routing primitives, and a testable codebase that can grow into a production-grade framework.

## Current capabilities

- Async `Bot` client
- `send_message`, `edit_message`, `delete_message`
- `get_me`, `get_chats`, `get_updates`, `get_subscriptions`
- Long polling runtime
- `Dispatcher` and `Router`
- `Command` filter
- `message.answer()` and `message.reply()`
- `RetryConfig` and `TimeoutConfig`
- test-friendly `FakeTransport`

## Installation

```bash
python -m pip install maxbotkit
```

For local development:

```bash
python -m pip install -e '.[dev]' --no-build-isolation
```

## Quickstart

```python
import asyncio
import os

from maxbotkit import Bot, Dispatcher, Router
from maxbotkit.filters import Command


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

## Client Configuration

`Bot` accepts a small but useful set of transport and reliability options:

```python
from maxbotkit import Bot, RetryConfig, TimeoutConfig

bot = Bot(
    token="TOKEN",
    base_url="https://platform-api.max.ru",
    verify_ssl=True,
    ca_file=None,
    timeout_config=TimeoutConfig(request_timeout=15.0),
    retry_config=RetryConfig(
        attempts=3,
        backoff_base=0.5,
        backoff_max=5.0,
        jitter=True,
    ),
)
```

### Configuration notes

- `base_url` can be replaced for internal deployments or fake API servers
- `verify_ssl=False` is useful only for local debugging
- `ca_file` can point to an internal CA bundle
- retries are applied only to retry-safe methods and retryable failures
- long polling requests automatically extend the underlying request timeout

## Core Client Methods

### Outgoing messages

```python
message = await bot.send_message(chat_id=123, text="Hello")

await bot.edit_message(
    message_id=message.message_id,
    text="Updated text",
)

await bot.delete_message(message_id=message.message_id)
```

### Bot and chat information

```python
me = await bot.get_me()
chats = await bot.get_chats(count=100)
subscriptions = await bot.get_subscriptions()
```

### Updates

```python
updates = await bot.get_updates(
    limit=100,
    timeout=30,
    types=["message_created"],
)
```

## Message Helpers

Inside handlers, incoming `Message` objects expose convenience helpers:

```python
@router.message(Command("start"))
async def start(message) -> None:
    await message.answer("Started")


@router.message()
async def echo(message) -> None:
    if message.text:
        await message.reply(f"Echo: {message.text}")
```

Current helper behavior:

- `message.answer(...)` sends a new message to the same chat
- `message.reply(...)` sends a linked reply to the concrete source message
- `message.message_id` exposes the MAX message ID (`mid`)

## Testing

`maxbotkit` includes a public fake transport for client tests:

```python
from maxbotkit import Bot
from maxbotkit.client.transport import TransportResponse
from maxbotkit.testing import FakeTransport

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

assert me.user_id == 1
assert transport.calls[0]["path"] == "/me"
```

This makes it easy to test:

- request serialization
- timeout and retry behavior
- error classification
- handler logic without talking to the real MAX API

## Public API

Current top-level imports:

```python
from maxbotkit import (
    Bot,
    MaxClient,
    Dispatcher,
    Router,
    Command,
    RetryConfig,
    TimeoutConfig,
    run_polling,
)
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

Build release artifacts:

```bash
python -m build
python -m twine check dist/*
```

## Examples

- [Echo Bot](examples/echo_bot/bot.py)
- [Client Basics](examples/client_basics/bot.py)
- [Testing Transport](examples/testing_transport/demo.py)

## Roadmap

`0.1.0` establishes the core API client layer. The next milestones focus on:

- stronger client typing
- broader MAX API coverage
- middleware and dependency injection
- richer filters
- observability and reliability layers

## Status

This project is currently pre-alpha and the public API is expected to evolve quickly.
