from __future__ import annotations

from typing import Any

import whenever as _whenever

from ._base import WheneverField


class MonthDayField(WheneverField):
    """Stores a :class:`~whenever.MonthDay` as a SQL ``SMALLINT`` (MMDD)."""

    whenever_type = _whenever.MonthDay
    stdlib_type = None

    def get_internal_type(self) -> str:
        return "SmallIntegerField"

    def _from_db(self, value: Any, connection: Any) -> _whenever.MonthDay:
        return _whenever.MonthDay(value // 100, value % 100)

    def _to_db(self, value: _whenever.MonthDay) -> int:
        return value.month * 100 + value.day

    def _parse(self, value: str) -> _whenever.MonthDay:
        return _whenever.MonthDay.parse_iso(value)

    def formfield(self, **kwargs: Any) -> Any:
        from ..forms.fields import MonthDayFormField

        defaults = {"form_class": MonthDayFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
