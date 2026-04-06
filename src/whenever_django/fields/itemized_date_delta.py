from __future__ import annotations

from typing import Any

import whenever as _whenever

from ._json_delta import _JsonDeltaField


class ItemizedDateDeltaField(_JsonDeltaField):
    """Stores a :class:`~whenever.ItemizedDateDelta` as JSON in a TEXT column.

    The JSON representation is a sparse dict containing only non-zero components.
    """

    whenever_type = _whenever.ItemizedDateDelta
    _allowed_keys = frozenset({"years", "months", "weeks", "days"})

    def formfield(self, **kwargs: Any) -> Any:
        from ..forms.fields import ItemizedDateDeltaFormField

        defaults = {"form_class": ItemizedDateDeltaFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
