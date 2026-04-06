from __future__ import annotations

import datetime as _stdlib
from typing import Any

import whenever as _whenever

from ._base import WheneverField


class PlainDateTimeField(WheneverField):
    """Stores a :class:`~whenever.PlainDateTime` as a naive timestamp.

    The database column is ``TIMESTAMP`` (no timezone). Aware datetimes
    are rejected.
    """

    whenever_type = _whenever.PlainDateTime
    stdlib_type = _stdlib.datetime

    def get_internal_type(self) -> str:
        return "DateTimeField"

    def _from_db(
        self, value: Any, connection: Any
    ) -> _whenever.PlainDateTime:
        if not isinstance(value, _stdlib.datetime):
            value = _stdlib.datetime.fromisoformat(str(value))
        if value.tzinfo is not None:
            value = value.replace(tzinfo=None)
        return _whenever.PlainDateTime(value)

    def _to_db(self, value: _whenever.PlainDateTime) -> _stdlib.datetime:
        return value.to_stdlib()

    def _parse(self, value: str) -> _whenever.PlainDateTime:
        return _whenever.PlainDateTime.parse_iso(value)

    def get_prep_value(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, self.whenever_type):
            return self._to_db(value)
        if self.from_stdlib and isinstance(value, _stdlib.datetime):
            if value.tzinfo is not None:
                raise TypeError(
                    "PlainDateTimeField does not accept aware datetimes. "
                    "Pass a naive datetime or a whenever.PlainDateTime."
                )
            return self._to_db(_whenever.PlainDateTime(value))
        if not isinstance(value, self.whenever_type):
            raise TypeError(
                f"PlainDateTimeField expects PlainDateTime, "
                f"got {type(value).__name__}. "
                f"Set from_stdlib=True to enable automatic coercion."
            )
        return self._to_db(value)

    def formfield(self, **kwargs: Any) -> Any:
        from ..forms.fields import PlainDateTimeFormField

        defaults = {"form_class": PlainDateTimeFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
