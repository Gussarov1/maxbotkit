from __future__ import annotations

from dataclasses import dataclass

from maxbotkit.methods.base import APIMethod


@dataclass(slots=True)
class GetUpdates(APIMethod):
    limit: int | None = None
    timeout: int | None = None
    marker: int | None = None
    types: list[str] | None = None

    http_method: str = "GET"
    path: str = "/updates"

    def __post_init__(self) -> None:
        if self.limit is not None and not 1 <= self.limit <= 1000:
            raise ValueError("limit must be between 1 and 1000.")
        if self.timeout is not None and not 0 <= self.timeout <= 90:
            raise ValueError("timeout must be between 0 and 90.")

    def build_params(self) -> dict[str, int | str | None]:
        return {
            "limit": self.limit,
            "timeout": self.timeout,
            "marker": self.marker,
            "types": ",".join(self.types) if self.types else None,
        }

    def request_timeout(self, default_timeout: float) -> float:
        if self.timeout is None:
            return default_timeout
        return max(default_timeout, float(self.timeout) + 5.0)
