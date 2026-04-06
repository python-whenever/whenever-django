from __future__ import annotations

import datetime as _stdlib
from typing import Any

import whenever as _whenever

from ._base import WheneverField


class WheneverDateField(WheneverField):
    """Stores a :class:`~whenever.Date` as a SQL ``DATE``."""

    whenever_type = _whenever.Date
    stdlib_type = _stdlib.date

    def get_internal_type(self) -> str:
        return "DateField"

    def _from_db(self, value: Any, connection: Any) -> _whenever.Date:
        if not isinstance(value, _stdlib.date):
            value = _stdlib.date.fromisoformat(str(value))
        return _whenever.Date(value)

    def _to_db(self, value: _whenever.Date) -> _stdlib.date:
        return value.to_stdlib()

    def _parse(self, value: str) -> _whenever.Date:
        return _whenever.Date.parse_iso(value)

    def formfield(self, **kwargs: Any) -> Any:
        from ..forms.fields import WheneverDateFormField

        defaults = {"form_class": WheneverDateFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
