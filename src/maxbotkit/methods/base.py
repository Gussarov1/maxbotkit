from __future__ import annotations

from typing import Any


class APIMethod:
    http_method: str
    path: str

    def build_params(self) -> dict[str, Any]:
        return {}

    def build_body(self) -> dict[str, Any]:
        return {}
