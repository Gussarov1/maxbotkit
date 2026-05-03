# Changelog

All notable changes to this project will be documented in this file.

## 0.1.0 - 2026-05-03

- Expanded the core MAX Bot API client around a reusable request pipeline.
- Added `send_message`, `edit_message`, `delete_message`, `get_me`, `get_chats`,
  `get_updates`, and `get_subscriptions`.
- Added `RetryConfig` and `TimeoutConfig`.
- Added safe retries for retryable transport failures and selected API errors.
- Added basic API error classification including unauthorized, forbidden, rate limit,
  not found, bad request, and server error variants.
- Added `MaxClient` alias for the low-level client layer.
- Added public testing utilities including `FakeTransport`.
- Added serialization-focused and resilience-focused tests.
- Expanded repository documentation and examples for the current client/runtime surface.

## 0.0.2 - 2026-05-03

- Cleaned up package metadata and branding to consistently use `maxbotkit`.
- Added `project.urls` for homepage, repository, issues, and changelog.
- Added `build` and `twine` to `dev` dependencies for local release workflows.
- Exported `maxbotkit.__version__`.
- Added a minimal `examples/echo_bot` application.
- Expanded README with example and release-build commands.

## 0.0.1 - 2026-05-03

- Bootstrapped the `maxbotkit` package with `src` layout and packaging metadata.
- Added a working async MAX Bot API client with core methods:
  `send_message`, `get_me`, `get_chats`, `get_updates`, `get_subscriptions`.
- Added polling runtime, dispatcher, router, and `Command` filter.
- Added `message.answer()` and `message.reply()` helpers.
- Added test coverage for client, polling, routing, and message helper flows.
- Added repository tooling for linting, type checking, pre-commit, and CI.
