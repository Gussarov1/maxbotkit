from __future__ import annotations

from dataclasses import dataclass

from maxbotkit.methods.base import APIMethod


@dataclass(slots=True)
class GetSubscriptions(APIMethod):
    http_method: str = "GET"
    path: str = "/subscriptions"
    safe_to_retry: bool = True
