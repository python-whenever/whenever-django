from __future__ import annotations

import datetime as _stdlib
from typing import Any

import whenever as _whenever

from ._base import WheneverField


class TimeDeltaField(WheneverField):
    """Stores a :class:`~whenever.TimeDelta` as microseconds in a BIGINT column.

    Compatible with Django's DurationField storage format.
    Nanosecond precision is silently truncated to microseconds.
    """

    whenever_type = _whenever.TimeDelta
    stdlib_type = _stdlib.timedelta

    def get_internal_type(self) -> str:
        return "BigIntegerField"

    def _from_db(self, value: Any, connection: Any) -> _whenever.TimeDelta:
        return _whenever.TimeDelta(microseconds=int(value))

    def _to_db(self, value: _whenever.TimeDelta) -> int:
        return int(value.total("microseconds"))

    def _parse(self, value: str) -> _whenever.TimeDelta:
        return _whenever.TimeDelta.parse_iso(value)

    def formfield(self, **kwargs: Any) -> Any:
        from ..forms.fields import TimeDeltaFormField

        defaults = {"form_class": TimeDeltaFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
