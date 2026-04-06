from __future__ import annotations

import json
from typing import Any

import whenever as _whenever

from ._base import WheneverField


class ItemizedDeltaField(WheneverField):
    """Stores a :class:`~whenever.ItemizedDelta` as JSON in a TEXT column.

    The JSON representation is a sparse dict containing only non-zero components.
    """

    whenever_type = _whenever.ItemizedDelta
    stdlib_type = None

    def get_internal_type(self) -> str:
        return "TextField"

    def _from_db(self, value: Any, connection: Any) -> _whenever.ItemizedDelta:
        return _whenever.ItemizedDelta(**json.loads(value))

    def _to_db(self, value: _whenever.ItemizedDelta) -> str:
        return json.dumps(dict(value))

    def _parse(self, value: str) -> _whenever.ItemizedDelta:
        return _whenever.ItemizedDelta.parse_iso(value)

    def formfield(self, **kwargs: Any) -> Any:
        from ..forms.fields import ItemizedDeltaFormField

        defaults = {"form_class": ItemizedDeltaFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
