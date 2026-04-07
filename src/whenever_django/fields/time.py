from __future__ import annotations

import datetime as _stdlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django import forms as _django_forms

import whenever as _whenever

from ._base import WheneverField


class WheneverTimeField(WheneverField):
    """Stores a :class:`~whenever.Time` as a SQL ``TIME``."""

    whenever_type = _whenever.Time
    stdlib_type = _stdlib.time

    def get_internal_type(self) -> str:
        return "TimeField"

    def _from_db(self, value: Any, connection: Any) -> _whenever.Time:
        if not isinstance(value, _stdlib.time):
            value = _stdlib.time.fromisoformat(str(value))
        return _whenever.Time(value)

    def _to_db(self, value: _whenever.Time) -> _stdlib.time:
        return value.to_stdlib()

    def _parse(self, value: str) -> _whenever.Time:
        return _whenever.Time.parse_iso(value)

    def formfield(
        self,
        form_class: type[_django_forms.Field] | None = None,
        choices_form_class: type[_django_forms.ChoiceField] | None = None,
        **kwargs: Any,
    ) -> _django_forms.Field | None:
        from ..forms.fields import WheneverTimeFormField

        return super().formfield(
            form_class=form_class or WheneverTimeFormField,
            choices_form_class=choices_form_class,
            **kwargs,
        )
