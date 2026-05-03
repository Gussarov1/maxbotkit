from __future__ import annotations

from dataclasses import fields
from typing import Any, TypeVar, cast

T = TypeVar("T", bound="BaseModel")


class BaseModel:
    """Small helper for dataclass-backed API models."""

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """Create a model instance from a dictionary, ignoring unknown keys."""
        field_names = {field.name for field in fields(cast(Any, cls))}
        payload = {key: value for key, value in data.items() if key in field_names}
        return cls(**payload)
