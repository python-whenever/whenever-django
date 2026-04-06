from __future__ import annotations

from typing import Any

import whenever as _whenever

from ._json_delta import _JsonDeltaField


class ItemizedDeltaField(_JsonDeltaField):
    """Stores a :class:`~whenever.ItemizedDelta` as JSON in a TEXT column.

    The JSON representation is a sparse dict containing only non-zero components.
    """

    whenever_type = _whenever.ItemizedDelta
    _allowed_keys = frozenset({
        "years", "months", "weeks", "days",
        "hours", "minutes", "seconds", "nanoseconds",
    })

    def formfield(self, **kwargs: Any) -> Any:
        from ..forms.fields import ItemizedDeltaFormField

        defaults = {"form_class": ItemizedDeltaFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
