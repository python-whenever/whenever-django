from __future__ import annotations

import datetime as _stdlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django import forms as _django_forms

import whenever as _whenever

from ._base import WheneverField


class WheneverDateField(WheneverField):
    """Stores a :class:`~whenever.Date` as a SQL ``DATE``."""

    whenever_type = _whenever.Date
    stdlib_type = _stdlib.date

    def get_internal_type(self) -> str:
        return "DateField"

    def _from_db(self, value: Any, connection: Any) -> _whenever.Date:
        if not isinstance(value, _stdlib.date):
            value = _stdlib.date.fromisoformat(str(value))
        return _whenever.Date(value)

    def _to_db(self, value: _whenever.Date) -> _stdlib.date:
        return value.to_stdlib()

    def _parse(self, value: str) -> _whenever.Date:
        return _whenever.Date.parse_iso(value)

    def formfield(
        self,
        form_class: type[_django_forms.Field] | None = None,
        choices_form_class: type[_django_forms.ChoiceField] | None = None,
        **kwargs: Any,
    ) -> _django_forms.Field | None:
        from ..forms.fields import WheneverDateFormField

        return super().formfield(
            form_class=form_class or WheneverDateFormField,
            choices_form_class=choices_form_class,
            **kwargs,
        )
