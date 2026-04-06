from __future__ import annotations

import datetime as _stdlib
from typing import Any

import whenever as _whenever

from ._base import WheneverField

_UTC = _stdlib.timezone.utc


class InstantField(WheneverField):
    """Stores a :class:`~whenever.Instant` as a timezone-aware timestamp.

    The database column is ``TIMESTAMP WITH TIME ZONE`` on PostgreSQL
    and ``TIMESTAMP`` on SQLite. Values are always stored in UTC.
    """

    whenever_type = _whenever.Instant
    stdlib_type = _stdlib.datetime

    def get_internal_type(self) -> str:
        return "DateTimeField"

    def _from_db(self, value: Any, connection: Any) -> _whenever.Instant:
        if not isinstance(value, _stdlib.datetime):
            value = _stdlib.datetime.fromisoformat(str(value))
        # Instant stores UTC by contract. SQLite and some backends return
        # naive datetimes — restoring UTC is safe because the column only
        # ever contains UTC values.
        if value.tzinfo is None:
            value = value.replace(tzinfo=_UTC)
        return _whenever.Instant(value)

    def _to_db(self, value: _whenever.Instant) -> _stdlib.datetime:
        return value.to_stdlib()

    def _parse(self, value: str) -> _whenever.Instant:
        return _whenever.Instant.parse_iso(value)

    def formfield(self, **kwargs: Any) -> Any:
        from ..forms.fields import InstantFormField

        defaults = {"form_class": InstantFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
