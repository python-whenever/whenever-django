from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django import forms as _django_forms

import whenever as _whenever

from ._json_delta import _JsonDeltaField


class ItemizedDateDeltaField(_JsonDeltaField):
    """Stores a :class:`~whenever.ItemizedDateDelta` as JSON in a TEXT column.

    The JSON representation is a sparse dict containing only non-zero components.
    """

    whenever_type = _whenever.ItemizedDateDelta
    _allowed_keys = frozenset({"years", "months", "weeks", "days"})

    def formfield(
        self,
        form_class: type[_django_forms.Field] | None = None,
        choices_form_class: type[_django_forms.ChoiceField] | None = None,
        **kwargs: Any,
    ) -> _django_forms.Field | None:
        from ..forms.fields import ItemizedDateDeltaFormField

        return super().formfield(
            form_class=form_class or ItemizedDateDeltaFormField,
            choices_form_class=choices_form_class,
            **kwargs,
        )
