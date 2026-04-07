from __future__ import annotations

import datetime as _stdlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django import forms as _django_forms

import whenever as _whenever

from ._composite import _CompositeWheneverField

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


class ZonedDateTimeField(_CompositeWheneverField):
    """Stores a :class:`~whenever.ZonedDateTime` as a UTC timestamp
    plus a paired IANA timezone name column.
    """

    whenever_type = _whenever.ZonedDateTime
    paired_suffix = "_tz"
    paired_max_length = 64
    compose_fn = staticmethod(_compose_zoned)
    decompose_fn = staticmethod(_decompose_zoned)

    def _to_db(self, value: _whenever.ZonedDateTime) -> _stdlib.datetime:
        return value.to_instant().to_stdlib()

    def _parse(self, value: str) -> _whenever.ZonedDateTime:
        return _whenever.ZonedDateTime.parse_iso(value)

    def formfield(
        self,
        form_class: type[_django_forms.Field] | None = None,
        choices_form_class: type[_django_forms.ChoiceField] | None = None,
        **kwargs: Any,
    ) -> _django_forms.Field | None:
        from ..forms.fields import ZonedDateTimeFormField

        return super().formfield(
            form_class=form_class or ZonedDateTimeFormField,
            choices_form_class=choices_form_class,
            **kwargs,
        )
