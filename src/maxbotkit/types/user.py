from __future__ import annotations

from dataclasses import dataclass

from maxbotkit.types.base import BaseModel


@dataclass(slots=True)
class User(BaseModel):
    """User or bot profile returned by MAX API methods."""

    user_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    is_bot: bool | None = None
    last_activity_time: int | None = None
    name: str | None = None
    description: str | None = None
    avatar_url: str | None = None
    full_avatar_url: str | None = None
    commands: list[dict[str, object]] | None = None
