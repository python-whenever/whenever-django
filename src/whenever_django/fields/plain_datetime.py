from __future__ import annotations

import datetime as _stdlib
import warnings
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
            warnings.warn(
                f"PlainDateTimeField received a timezone-aware datetime "
                f"(tzinfo={value.tzinfo}). Timezone info is being discarded. "
                f"If this column stores UTC timestamps, consider using "
                f"InstantField instead.",
                UserWarning,
                stacklevel=2,
            )
            value = value.replace(tzinfo=None)
        return _whenever.PlainDateTime(value)

    def _to_db(self, value: _whenever.PlainDateTime) -> _stdlib.datetime:
        return value.to_stdlib()

    def _parse(self, value: str) -> _whenever.PlainDateTime:
        return _whenever.PlainDateTime.parse_iso(value)

    def get_prep_value(self, value: Any) -> Any:
        if value is None:
            return None
        if self.from_stdlib and isinstance(value, _stdlib.datetime):
            if value.tzinfo is not None:
                raise TypeError(
                    "PlainDateTimeField does not accept aware datetimes. "
                    "Pass a naive datetime or a whenever.PlainDateTime."
                )
        return super().get_prep_value(value)

    def formfield(self, **kwargs: Any) -> Any:
        from ..forms.fields import PlainDateTimeFormField

        defaults = {"form_class": PlainDateTimeFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
