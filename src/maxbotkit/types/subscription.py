from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from maxbotkit.types.base import BaseModel


@dataclass(slots=True)
class Subscription(BaseModel):
    url: str | None = None
    time: int | None = None
    update_types: list[str] | None = None
    version: str | None = None
    secret_key: str | None = None


@dataclass(slots=True)
class SubscriptionList(BaseModel):
    subscriptions: list[Subscription]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SubscriptionList":
        items = data.get("subscriptions", [])
        subscriptions = [Subscription.from_dict(item) for item in items if isinstance(item, dict)]
        return cls(subscriptions=subscriptions)
