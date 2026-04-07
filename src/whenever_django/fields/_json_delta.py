from __future__ import annotations

import json
from typing import Any

from django.core.exceptions import ValidationError

from ._base import WheneverField


class _JsonDeltaField(WheneverField):
    """Base for fields that store whenever delta types as JSON in a TEXT column.

    Subclasses set ``whenever_type``, ``_allowed_keys``, and provide
    ``formfield``.
    """

    stdlib_type = None
    _allowed_keys: frozenset[str]

    def get_internal_type(self) -> str:
        return "TextField"

    def _from_db(self, value: Any, connection: Any) -> Any:
        data = json.loads(value)
        if not isinstance(data, dict) or not data.keys() <= self._allowed_keys:
            raise ValidationError(
                f"Corrupt {self.whenever_type.__name__} JSON in database: "
                f"expected a dict with keys from "
                f"{sorted(self._allowed_keys)}."
            )
        constructor: Any = self.whenever_type
        return constructor(**data)

    def _to_db(self, value: Any) -> str:
        return json.dumps(dict(value))

    def _parse(self, value: str) -> Any:
        return self.whenever_type.parse_iso(value)
