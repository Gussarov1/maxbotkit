from __future__ import annotations

import asyncio

from maxbotkit._internal.typing import MethodLike
from maxbotkit.client.transport import BaseTransport, TransportResponse, UrllibTransport
from maxbotkit.config import RetryConfig, TimeoutConfig
from maxbotkit.exceptions.api import APIError, RateLimitError, ServerError
from maxbotkit.exceptions.transport import RetryableTransportError
from maxbotkit.methods.delete_message import DeleteMessage
from maxbotkit.methods.edit_message import EditMessage
from maxbotkit.methods.get_chats import GetChats
from maxbotkit.methods.get_me import GetMe
from maxbotkit.methods.get_subscriptions import GetSubscriptions
from maxbotkit.methods.get_updates import GetUpdates
from maxbotkit.methods.send_message import SendMessage
from maxbotkit.types.chat import ChatList
from maxbotkit.types.message import Message
from maxbotkit.types.subscription import SubscriptionList
from maxbotkit.types.update import UpdateList
from maxbotkit.types.user import User


class Bot:
    """Async MAX Bot API client with basic reliability and testing hooks.

    Args:
        token: Bot token used for the ``Authorization`` header.
        base_url: Base MAX API URL. Override this for internal or test setups.
        transport: Custom transport implementation. When omitted, the default
            urllib-based transport is used.
        timeout: Fallback request timeout in seconds when no timeout config is
            provided.
        timeout_config: Structured timeout settings.
        retry_config: Structured retry settings for retry-safe methods.
        verify_ssl: Whether TLS certificates should be verified.
        ca_file: Optional path to a custom CA bundle.
    """

    def __init__(
        self,
        token: str,
        *,
        base_url: str = "https://platform-api.max.ru",
        transport: BaseTransport | None = None,
        timeout: float = 10.0,
        timeout_config: TimeoutConfig | None = None,
        retry_config: RetryConfig | None = None,
        verify_ssl: bool = True,
        ca_file: str | None = None,
    ) -> None:
        self.token = token
        self.base_url = base_url
        self.transport = transport or UrllibTransport(verify_ssl=verify_ssl, ca_file=ca_file)
        self.timeout_config = timeout_config or TimeoutConfig(request_timeout=timeout)
        self.retry_config = retry_config or RetryConfig()

    async def send_message(
        self,
        *,
        text: str,
        chat_id: int | None = None,
        user_id: int | None = None,
        notify: bool = True,
        disable_link_preview: bool | None = None,
        format: str | None = None,
        link: dict[str, str] | None = None,
    ) -> Message:
        """Send a text message to a chat or user.

        Exactly one of ``chat_id`` or ``user_id`` must be provided.
        """
        method = SendMessage(
            text=text,
            chat_id=chat_id,
            user_id=user_id,
            notify=notify,
            disable_link_preview=disable_link_preview,
            format=format,
            link=link,
        )

        response = await self._request(method)

        return Message.from_api_response(response.body, bot=self)

    async def edit_message(
        self,
        *,
        message_id: str,
        text: str,
        notify: bool = True,
        format: str | None = None,
        link: dict[str, str] | None = None,
    ) -> bool:
        """Edit an existing message by its MAX message identifier."""
        method = EditMessage(
            message_id=message_id,
            text=text,
            notify=notify,
            format=format,
            link=link,
        )

        response = await self._request(method)
        if isinstance(response.body, dict):
            return bool(response.body.get("success"))
        return False

    async def delete_message(
        self,
        *,
        message_id: str,
    ) -> bool:
        """Delete a message by its MAX message identifier."""
        method = DeleteMessage(message_id=message_id)

        response = await self._request(method)
        if isinstance(response.body, dict):
            return bool(response.body.get("success"))
        return False

    async def get_chats(
        self,
        *,
        count: int | None = None,
        marker: int | None = None,
    ) -> ChatList:
        """Return chats visible to the bot."""
        method = GetChats(count=count, marker=marker)

        response = await self._request(method)

        return ChatList.from_dict(response.body)

    async def get_me(self) -> User:
        """Return information about the current bot account."""
        method = GetMe()

        response = await self._request(method)

        return User.from_dict(response.body)

    async def get_updates(
        self,
        *,
        limit: int | None = None,
        timeout: int | None = None,
        marker: int | None = None,
        types: list[str] | None = None,
    ) -> UpdateList:
        """Fetch updates using the MAX long-polling API."""
        method = GetUpdates(
            limit=limit,
            timeout=timeout,
            marker=marker,
            types=types,
        )

        response = await self._request(method)

        return UpdateList.from_dict(response.body, bot=self)

    async def get_subscriptions(self) -> SubscriptionList:
        """Return webhook subscriptions currently configured for the bot."""
        method = GetSubscriptions()

        response = await self._request(method)

        return SubscriptionList.from_dict(response.body)

    async def _request(self, method: MethodLike) -> TransportResponse:
        attempts = self.retry_config.attempts
        last_error: Exception | None = None

        for attempt_index in range(attempts):
            try:
                json_body = method.build_body()
                request_params = dict(method.build_params())
                request_body: dict[str, object] | None = dict(json_body) if json_body else None
                response = await self.transport.request(
                    method=method.http_method,
                    base_url=self.base_url,
                    path=method.path,
                    params=request_params,
                    json_body=request_body,
                    headers={"Authorization": self.token},
                    timeout=float(method.request_timeout(self.timeout_config.request_timeout)),
                )
            except RetryableTransportError as exc:
                last_error = exc
                if not method.safe_to_retry or attempt_index == attempts - 1:
                    raise
                await asyncio.sleep(self.retry_config.backoff_for_attempt(attempt_index))
                continue

            if response.status_code < 400:
                return response

            error = APIError.from_response(response.status_code, response.body)
            if self._should_retry_api_error(
                method=method,
                error=error,
                attempt_index=attempt_index,
            ):
                last_error = error
                await asyncio.sleep(self.retry_config.backoff_for_attempt(attempt_index))
                continue
            raise error

        if last_error is not None:
            raise last_error
        raise RuntimeError("Request finished without response or error.")

    def _should_retry_api_error(
        self,
        *,
        method: MethodLike,
        error: APIError,
        attempt_index: int,
    ) -> bool:
        if not method.safe_to_retry:
            return False
        if attempt_index >= self.retry_config.attempts - 1:
            return False
        return isinstance(error, (RateLimitError, ServerError))


class MaxClient(Bot):
    """Backward-compatible alias for the low-level MAX API client."""
