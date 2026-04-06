from __future__ import annotations

import datetime as _stdlib
from typing import Any

import whenever as _whenever
from django.core.exceptions import ValidationError
from django.db import models

from ._base import WheneverField
from ..descriptors import CompositeFieldDescriptor

_UTC = _stdlib.timezone.utc


def _compose_zoned(
    dt_value: Any, tz_name: str | None
) -> _whenever.ZonedDateTime | None:
    if dt_value is None or tz_name is None:
        return None
    if not isinstance(dt_value, _stdlib.datetime):
        dt_value = _stdlib.datetime.fromisoformat(str(dt_value))
    if dt_value.tzinfo is None:
        dt_value = dt_value.replace(tzinfo=_UTC)
    instant = _whenever.Instant(dt_value)
    return instant.to_tz(tz_name)


def _decompose_zoned(
    value: _whenever.ZonedDateTime,
) -> tuple[_stdlib.datetime, str]:
    return value.to_instant().to_stdlib(), value.tz


class ZonedDateTimeField(WheneverField):
    """Stores a :class:`~whenever.ZonedDateTime` as a UTC timestamp
    plus a paired IANA timezone name column.
    """

    whenever_type = _whenever.ZonedDateTime
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

        tz_field = models.CharField(
            max_length=64,
            null=self.null,
            blank=self.blank,
            editable=False,
        )
        # Ensure paired field appears before the main field in _meta.fields
        tz_field.creation_counter = self.creation_counter - 1
        tz_attname = f"{self.attname}_tz"
        cls.add_to_class(tz_attname, tz_field)

        descriptor = CompositeFieldDescriptor(
            field=self,
            paired_attname=tz_attname,
            compose=_compose_zoned,
            decompose=_decompose_zoned,
        )
        setattr(cls, self.name, descriptor)

    def _from_db(
        self, value: Any, connection: Any
    ) -> _stdlib.datetime:
        # Return raw datetime — the descriptor composes the final ZonedDateTime
        if not isinstance(value, _stdlib.datetime):
            value = _stdlib.datetime.fromisoformat(str(value))
        if value.tzinfo is None:
            value = value.replace(tzinfo=_UTC)
        return value

    def _to_db(self, value: _whenever.ZonedDateTime) -> _stdlib.datetime:
        return value.to_instant().to_stdlib()

    def _parse(self, value: str) -> _whenever.ZonedDateTime:
        return _whenever.ZonedDateTime.parse_iso(value)

    def get_prep_value(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, _whenever.ZonedDateTime):
            return self._to_db(value)
        # Accept stdlib datetime from pre_save path
        if isinstance(value, _stdlib.datetime):
            return value
        raise TypeError(
            f"ZonedDateTimeField expects ZonedDateTime, "
            f"got {type(value).__name__}."
        )

    def pre_save(self, model_instance: Any, add: bool) -> Any:
        value = model_instance.__dict__.get(self.attname)
        if value is None:
            return None
        if isinstance(value, _whenever.ZonedDateTime):
            tz_attname = f"{self.attname}_tz"
            model_instance.__dict__[tz_attname] = value.tz
            return self._to_db(value)
        # stdlib datetime from DB reload — paired column already set
        if isinstance(value, _stdlib.datetime):
            return value
        raise TypeError(
            f"ZonedDateTimeField expects ZonedDateTime, "
            f"got {type(value).__name__}."
        )

    def from_db_value(
        self, value: Any, expression: Any, connection: Any
    ) -> Any:
        if value is None:
            return None
        # Return raw value — the descriptor handles composition
        return self._from_db(value, connection)

    def deconstruct(self) -> tuple[str, str, list[Any], dict[str, Any]]:
        name, path, args, kwargs = super().deconstruct()
        # Paired field is recreated by contribute_to_class
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
            f"Cannot convert {type(value).__name__} to ZonedDateTime."
        )

    def formfield(self, **kwargs: Any) -> Any:
        from ..forms.fields import ZonedDateTimeFormField

        defaults = {"form_class": ZonedDateTimeFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def value_to_string(self, obj: Any) -> str:
        value = getattr(obj, self.name, None)
        if value is None:
            return ""
        if isinstance(value, _whenever.ZonedDateTime):
            return str(value)
        return str(value)
