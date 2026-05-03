from __future__ import annotations

from dataclasses import dataclass

from maxbotkit.methods.base import APIMethod


@dataclass(slots=True)
class GetChats(APIMethod):
    count: int | None = None
    marker: int | None = None

    http_method: str = "GET"
    path: str = "/chats"

    def __post_init__(self) -> None:
        if self.count is not None and not 1 <= self.count <= 100:
            raise ValueError("count must be between 1 and 100.")

    def build_params(self) -> dict[str, int | None]:
        return {
            "count": self.count,
            "marker": self.marker,
        }
