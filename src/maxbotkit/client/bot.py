from __future__ import annotations

from maxbotkit.client.transport import BaseTransport, UrllibTransport
from maxbotkit.exceptions.api import APIError
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
    def __init__(
        self,
        token: str,
        *,
        base_url: str = "https://platform-api.max.ru",
        transport: BaseTransport | None = None,
        timeout: float = 10.0,
        verify_ssl: bool = True,
        ca_file: str | None = None,
    ) -> None:
        self.token = token
        self.base_url = base_url
        self.transport = transport or UrllibTransport(verify_ssl=verify_ssl, ca_file=ca_file)
        self.timeout = timeout

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
        method = SendMessage(
            text=text,
            chat_id=chat_id,
            user_id=user_id,
            notify=notify,
            disable_link_preview=disable_link_preview,
            format=format,
            link=link,
        )

        response = await self.transport.request(
            method=method.http_method,
            base_url=self.base_url,
            path=method.path,
            params=method.build_params(),
            json_body=method.build_body(),
            headers={"Authorization": self.token},
            timeout=self.timeout,
        )

        if response.status_code >= 400:
            raise APIError.from_response(response.status_code, response.body)

        return Message.from_api_response(response.body, bot=self)

    async def get_chats(
        self,
        *,
        count: int | None = None,
        marker: int | None = None,
    ) -> ChatList:
        method = GetChats(count=count, marker=marker)

        response = await self.transport.request(
            method=method.http_method,
            base_url=self.base_url,
            path=method.path,
            params=method.build_params(),
            json_body=None,
            headers={"Authorization": self.token},
            timeout=self.timeout,
        )

        if response.status_code >= 400:
            raise APIError.from_response(response.status_code, response.body)

        return ChatList.from_dict(response.body)

    async def get_me(self) -> User:
        method = GetMe()

        response = await self.transport.request(
            method=method.http_method,
            base_url=self.base_url,
            path=method.path,
            params=method.build_params(),
            json_body=None,
            headers={"Authorization": self.token},
            timeout=self.timeout,
        )

        if response.status_code >= 400:
            raise APIError.from_response(response.status_code, response.body)

        return User.from_dict(response.body)

    async def get_updates(
        self,
        *,
        limit: int | None = None,
        timeout: int | None = None,
        marker: int | None = None,
        types: list[str] | None = None,
    ) -> UpdateList:
        method = GetUpdates(
            limit=limit,
            timeout=timeout,
            marker=marker,
            types=types,
        )

        response = await self.transport.request(
            method=method.http_method,
            base_url=self.base_url,
            path=method.path,
            params=method.build_params(),
            json_body=None,
            headers={"Authorization": self.token},
            timeout=float(method.request_timeout(self.timeout)),
        )

        if response.status_code >= 400:
            raise APIError.from_response(response.status_code, response.body)

        return UpdateList.from_dict(response.body, bot=self)

    async def get_subscriptions(self) -> SubscriptionList:
        method = GetSubscriptions()

        response = await self.transport.request(
            method=method.http_method,
            base_url=self.base_url,
            path=method.path,
            params=method.build_params(),
            json_body=None,
            headers={"Authorization": self.token},
            timeout=self.timeout,
        )

        if response.status_code >= 400:
            raise APIError.from_response(response.status_code, response.body)

        return SubscriptionList.from_dict(response.body)
