from __future__ import annotations

import asyncio
import json
import ssl
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request

from maxbotkit.exceptions.transport import RetryableTransportError, TransportError


@dataclass(slots=True)
class TransportResponse:
    """Low-level HTTP response wrapper used by transports."""

    status_code: int
    body: Any
    headers: dict[str, str]


class BaseTransport:
    """Abstract transport used by :class:`maxbotkit.client.bot.Bot`."""

    async def request(
        self,
        *,
        method: str,
        base_url: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 10.0,
    ) -> TransportResponse:
        """Execute a single HTTP request against the MAX API."""
        raise NotImplementedError


class UrllibTransport(BaseTransport):
    """Default transport implementation backed by the Python standard library."""

    def __init__(
        self,
        *,
        verify_ssl: bool = True,
        ca_file: str | None = None,
    ) -> None:
        self.verify_ssl = verify_ssl
        self.ca_file = ca_file

    async def request(
        self,
        *,
        method: str,
        base_url: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 10.0,
    ) -> TransportResponse:
        return await asyncio.to_thread(
            self._request_sync,
            method=method,
            base_url=base_url,
            path=path,
            params=params,
            json_body=json_body,
            headers=headers,
            timeout=timeout,
        )

    def _request_sync(
        self,
        *,
        method: str,
        base_url: str,
        path: str,
        params: dict[str, Any] | None,
        json_body: dict[str, Any] | None,
        headers: dict[str, str] | None,
        timeout: float,
    ) -> TransportResponse:
        query = parse.urlencode({k: v for k, v in (params or {}).items() if v is not None})
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        if query:
            url = f"{url}?{query}"

        payload = None
        request_headers = dict(headers or {})
        if json_body is not None:
            payload = json.dumps(json_body).encode("utf-8")
            request_headers.setdefault("Content-Type", "application/json")

        req = request.Request(url=url, data=payload, headers=request_headers, method=method.upper())

        try:
            ssl_context = self._build_ssl_context()
            with request.urlopen(req, timeout=timeout, context=ssl_context) as response:
                raw_body = response.read().decode("utf-8")
                return TransportResponse(
                    status_code=response.status,
                    body=self._decode_body(raw_body),
                    headers=dict(response.headers.items()),
                )
        except error.HTTPError as exc:
            raw_body = exc.read().decode("utf-8")
            return TransportResponse(
                status_code=exc.code,
                body=self._decode_body(raw_body),
                headers=dict(exc.headers.items()),
            )
        except TimeoutError as exc:
            raise RetryableTransportError(str(exc)) from exc
        except error.URLError as exc:
            raise RetryableTransportError(str(exc)) from exc
        except OSError as exc:
            raise TransportError(str(exc)) from exc

    @staticmethod
    def _decode_body(raw_body: str) -> Any:
        if not raw_body:
            return None
        try:
            return json.loads(raw_body)
        except json.JSONDecodeError:
            return raw_body

    def _build_ssl_context(self) -> ssl.SSLContext:
        if not self.verify_ssl:
            return ssl._create_unverified_context()

        if self.ca_file is not None:
            return ssl.create_default_context(cafile=self.ca_file)

        return ssl.create_default_context()
