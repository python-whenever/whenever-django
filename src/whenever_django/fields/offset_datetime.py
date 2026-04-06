from __future__ import annotations

import datetime as _stdlib
import re
from typing import Any

import whenever as _whenever

from ._composite import _CompositeWheneverField

_UTC = _stdlib.timezone.utc
_OFFSET_RE = re.compile(r"^[+-]\d{2}:\d{2}$")


def _offset_to_string(offset: _whenever.TimeDelta) -> str:
    """Format a TimeDelta offset as ±HH:MM."""
    total_secs = int(offset.total("seconds"))
    sign = "+" if total_secs >= 0 else "-"
    abs_secs = abs(total_secs)
    hh = abs_secs // 3600
    mm = (abs_secs % 3600) // 60
    return f"{sign}{hh:02d}:{mm:02d}"


def _string_to_offset(s: str) -> _whenever.TimeDelta:
    """Parse ±HH:MM string back to a TimeDelta."""
    if not _OFFSET_RE.match(s):
        raise ValueError(f"Invalid UTC offset format: {s!r}")
    sign = -1 if s[0] == "-" else 1
    parts = s.lstrip("+-").split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    return _whenever.TimeDelta(hours=sign * hours, minutes=sign * minutes)


def _compose_offset(
    dt_value: Any, offset_str: str | None
) -> _whenever.OffsetDateTime | None:
    if dt_value is None or offset_str is None:
        return None
    if not isinstance(dt_value, _stdlib.datetime):
        dt_value = _stdlib.datetime.fromisoformat(str(dt_value))
    if dt_value.tzinfo is None:
        dt_value = dt_value.replace(tzinfo=_UTC)
    instant = _whenever.Instant(dt_value)
    offset = _string_to_offset(offset_str)
    return instant.to_fixed_offset(offset)


def _decompose_offset(
    value: _whenever.OffsetDateTime,
) -> tuple[_stdlib.datetime, str]:
    return value.to_instant().to_stdlib(), _offset_to_string(value.offset)


class OffsetDateTimeField(_CompositeWheneverField):
    """Stores a :class:`~whenever.OffsetDateTime` as a UTC timestamp
    plus a paired UTC offset column in ±HH:MM format.
    """

    whenever_type = _whenever.OffsetDateTime
    paired_suffix = "_offset"
    paired_max_length = 6
    compose_fn = staticmethod(_compose_offset)
    decompose_fn = staticmethod(_decompose_offset)

    def _to_db(self, value: _whenever.OffsetDateTime) -> _stdlib.datetime:
        return value.to_instant().to_stdlib()

    def _parse(self, value: str) -> _whenever.OffsetDateTime:
        return _whenever.OffsetDateTime.parse_iso(value)

    def formfield(self, **kwargs: Any) -> Any:
        from ..forms.fields import OffsetDateTimeFormField

        defaults = {"form_class": OffsetDateTimeFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
