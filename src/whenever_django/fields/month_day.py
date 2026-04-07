from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django import forms as _django_forms

import whenever as _whenever

from ._base import WheneverField


class MonthDayField(WheneverField):
    """Stores a :class:`~whenever.MonthDay` as a SQL ``SMALLINT`` (MMDD)."""

    whenever_type = _whenever.MonthDay
    stdlib_type = None

    def get_internal_type(self) -> str:
        return "SmallIntegerField"

    def _from_db(self, value: Any, connection: Any) -> _whenever.MonthDay:
        return _whenever.MonthDay(value // 100, value % 100)

    def _to_db(self, value: _whenever.MonthDay) -> int:
        return value.month * 100 + value.day

    def _parse(self, value: str) -> _whenever.MonthDay:
        return _whenever.MonthDay.parse_iso(value)

    def formfield(
        self,
        form_class: type[_django_forms.Field] | None = None,
        choices_form_class: type[_django_forms.ChoiceField] | None = None,
        **kwargs: Any,
    ) -> _django_forms.Field | None:
        from ..forms.fields import MonthDayFormField

        return super().formfield(
            form_class=form_class or MonthDayFormField,
            choices_form_class=choices_form_class,
            **kwargs,
        )
