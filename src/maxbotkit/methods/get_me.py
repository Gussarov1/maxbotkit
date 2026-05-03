from __future__ import annotations

from dataclasses import dataclass

from maxbotkit.methods.base import APIMethod


@dataclass(slots=True)
class GetMe(APIMethod):
    http_method: str = "GET"
    path: str = "/me"
