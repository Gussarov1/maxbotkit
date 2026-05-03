# Changelog

All notable changes to this project will be documented in this file.

## 0.0.1 - 2026-05-03

- Bootstrapped the `maxbotkit` package with `src` layout and packaging metadata.
- Added a working async MAX Bot API client with core methods:
  `send_message`, `get_me`, `get_chats`, `get_updates`, `get_subscriptions`.
- Added polling runtime, dispatcher, router, and `Command` filter.
- Added `message.answer()` and `message.reply()` helpers.
- Added test coverage for client, polling, routing, and message helper flows.
- Added repository tooling for linting, type checking, pre-commit, and CI.
