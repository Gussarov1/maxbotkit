from __future__ import annotations

from dataclasses import fields
from typing import Any, TypeVar

T = TypeVar("T", bound="BaseModel")


class BaseModel:
    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        field_names = {field.name for field in fields(cls)}
        payload = {key: value for key, value in data.items() if key in field_names}
        return cls(**payload)
