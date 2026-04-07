from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django import forms as _django_forms

import whenever as _whenever

from ._base import WheneverField


class YearMonthField(WheneverField):
    """Stores a :class:`~whenever.YearMonth` as a SQL ``INTEGER`` (YYYYMM)."""

    whenever_type = _whenever.YearMonth
    stdlib_type = None

    def get_internal_type(self) -> str:
        return "IntegerField"

    def _from_db(self, value: Any, connection: Any) -> _whenever.YearMonth:
        return _whenever.YearMonth(value // 100, value % 100)

    def _to_db(self, value: _whenever.YearMonth) -> int:
        return value.year * 100 + value.month

    def _parse(self, value: str) -> _whenever.YearMonth:
        return _whenever.YearMonth.parse_iso(value)

    def formfield(
        self,
        form_class: type[_django_forms.Field] | None = None,
        choices_form_class: type[_django_forms.ChoiceField] | None = None,
        **kwargs: Any,
    ) -> _django_forms.Field | None:
        from ..forms.fields import YearMonthFormField

        return super().formfield(
            form_class=form_class or YearMonthFormField,
            choices_form_class=choices_form_class,
            **kwargs,
        )
