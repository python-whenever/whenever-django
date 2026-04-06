from __future__ import annotations

from typing import Any

import whenever as _whenever

from ._base import WheneverField


class YearMonthField(WheneverField):
    """Stores a :class:`~whenever.YearMonth` as a SQL ``INTEGER`` (YYYYMM)."""

    whenever_type = _whenever.YearMonth
    stdlib_type = None

    def get_internal_type(self) -> str:
        return "IntegerField"

    def _from_db(self, value: Any, connection: Any) -> _whenever.YearMonth:
        return _whenever.YearMonth(value // 100, value % 100)

    def _to_db(self, value: _whenever.YearMonth) -> int:
        return value.year * 100 + value.month

    def _parse(self, value: str) -> _whenever.YearMonth:
        return _whenever.YearMonth.parse_iso(value)

    def formfield(self, **kwargs: Any) -> Any:
        from ..forms.fields import YearMonthFormField

        defaults = {"form_class": YearMonthFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
