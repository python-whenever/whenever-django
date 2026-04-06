from __future__ import annotations

import datetime as _stdlib
from typing import Any

import whenever as _whenever

from ._base import WheneverField


class WheneverTimeField(WheneverField):
    """Stores a :class:`~whenever.Time` as a SQL ``TIME``."""

    whenever_type = _whenever.Time
    stdlib_type = _stdlib.time

    def get_internal_type(self) -> str:
        return "TimeField"

    def _from_db(self, value: Any, connection: Any) -> _whenever.Time:
        if not isinstance(value, _stdlib.time):
            value = _stdlib.time.fromisoformat(str(value))
        return _whenever.Time(value)

    def _to_db(self, value: _whenever.Time) -> _stdlib.time:
        return value.to_stdlib()

    def _parse(self, value: str) -> _whenever.Time:
        return _whenever.Time.parse_iso(value)

    def formfield(self, **kwargs: Any) -> Any:
        from ..forms.fields import WheneverTimeFormField

        defaults = {"form_class": WheneverTimeFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
