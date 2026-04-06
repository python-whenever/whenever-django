from __future__ import annotations

import datetime as _stdlib
from typing import Any

import whenever as _whenever
from django.core.exceptions import ValidationError
from django.db import models

from ._base import WheneverField
from ..descriptors import CompositeFieldDescriptor

_UTC = _stdlib.timezone.utc


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
    sign = -1 if s[0] == "-" else 1
    parts = s.lstrip("+-").split(":")
    hours = int(parts[0])
    minutes = int(parts[1]) if len(parts) > 1 else 0
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


class OffsetDateTimeField(WheneverField):
    """Stores a :class:`~whenever.OffsetDateTime` as a UTC timestamp
    plus a paired UTC offset column in ±HH:MM format.
    """

    whenever_type = _whenever.OffsetDateTime
    stdlib_type = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("from_stdlib", False)
        super().__init__(*args, **kwargs)

    def get_internal_type(self) -> str:
        return "DateTimeField"

    def contribute_to_class(
        self, cls: type, name: str, **kwargs: Any
    ) -> None:
        super().contribute_to_class(cls, name, **kwargs)

        offset_field = models.CharField(
            max_length=6,
            null=self.null,
            blank=self.blank,
            editable=False,
        )
        offset_field.creation_counter = self.creation_counter - 1
        offset_attname = f"{self.attname}_offset"
        cls.add_to_class(offset_attname, offset_field)

        descriptor = CompositeFieldDescriptor(
            field=self,
            paired_attname=offset_attname,
            compose=_compose_offset,
            decompose=_decompose_offset,
        )
        setattr(cls, self.name, descriptor)

    def _from_db(
        self, value: Any, connection: Any
    ) -> _stdlib.datetime:
        if not isinstance(value, _stdlib.datetime):
            value = _stdlib.datetime.fromisoformat(str(value))
        if value.tzinfo is None:
            value = value.replace(tzinfo=_UTC)
        return value

    def _to_db(self, value: _whenever.OffsetDateTime) -> _stdlib.datetime:
        return value.to_instant().to_stdlib()

    def _parse(self, value: str) -> _whenever.OffsetDateTime:
        return _whenever.OffsetDateTime.parse_iso(value)

    def get_prep_value(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, _whenever.OffsetDateTime):
            return self._to_db(value)
        if isinstance(value, _stdlib.datetime):
            return value
        raise TypeError(
            f"OffsetDateTimeField expects OffsetDateTime, "
            f"got {type(value).__name__}."
        )

    def pre_save(self, model_instance: Any, add: bool) -> Any:
        value = model_instance.__dict__.get(self.attname)
        if value is None:
            return None
        if isinstance(value, _whenever.OffsetDateTime):
            offset_attname = f"{self.attname}_offset"
            model_instance.__dict__[offset_attname] = _offset_to_string(value.offset)
            return self._to_db(value)
        if isinstance(value, _stdlib.datetime):
            return value
        raise TypeError(
            f"OffsetDateTimeField expects OffsetDateTime, "
            f"got {type(value).__name__}."
        )

    def from_db_value(
        self, value: Any, expression: Any, connection: Any
    ) -> Any:
        if value is None:
            return None
        return self._from_db(value, connection)

    def deconstruct(self) -> tuple[str, str, list[Any], dict[str, Any]]:
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs

    def to_python(self, value: Any) -> Any:
        if value is None or isinstance(value, self.whenever_type):
            return value
        if isinstance(value, str):
            try:
                return self._parse(value)
            except (ValueError, TypeError) as e:
                raise ValidationError(
                    f"Invalid value for {self.__class__.__name__}: {e}"
                ) from e
        raise ValidationError(
            f"Cannot convert {type(value).__name__} to OffsetDateTime."
        )

    def formfield(self, **kwargs: Any) -> Any:
        from ..forms.fields import OffsetDateTimeFormField

        defaults = {"form_class": OffsetDateTimeFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def value_to_string(self, obj: Any) -> str:
        value = getattr(obj, self.name, None)
        if value is None:
            return ""
        if isinstance(value, _whenever.OffsetDateTime):
            return str(value)
        return str(value)
