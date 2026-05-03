from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from maxbotkit.client.transport import TransportResponse
    from maxbotkit.types.message import Message
    from maxbotkit.types.update import UpdateList


class BotLike(Protocol):
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
    ) -> Message: ...

    async def get_updates(
        self,
        *,
        limit: int | None = None,
        timeout: int | None = None,
        marker: int | None = None,
        types: list[str] | None = None,
    ) -> UpdateList: ...


class MethodLike(Protocol):
    http_method: str
    path: str
    safe_to_retry: bool

    def build_params(self) -> dict[str, object]: ...

    def build_body(self) -> dict[str, object]: ...

    def request_timeout(self, default_timeout: float) -> float: ...


class TransportLike(Protocol):
    async def request(
        self,
        *,
        method: str,
        base_url: str,
        path: str,
        params: dict[str, object] | None = None,
        json_body: dict[str, object] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 10.0,
    ) -> TransportResponse: ...
