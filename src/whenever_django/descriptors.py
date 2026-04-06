from __future__ import annotations

from typing import Any


class CompositeFieldDescriptor:
    """Descriptor for composite fields that span two DB columns.

    Handles the main column (datetime) and a paired metadata column
    (timezone name or UTC offset). Presents a single whenever object
    to Python while storing two separate DB columns.
    """

    def __init__(
        self,
        field: Any,
        paired_attname: str,
        compose: Any,
        decompose: Any,
    ) -> None:
        self.field = field
        self.attname = field.attname
        self.paired_attname = paired_attname
        # compose(dt_value, meta_value) -> whenever object
        self.compose = compose
        # decompose(whenever_value) -> (dt_value, meta_value)
        self.decompose = decompose

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        if instance is None:
            return self

        # Deferred field check — if attname not loaded, trigger refresh
        if self.attname not in instance.__dict__:
            instance.refresh_from_db(fields=[self.attname, self.paired_attname])

        dt_val = instance.__dict__.get(self.attname)
        meta_val = instance.__dict__.get(self.paired_attname)

        if dt_val is None:
            return None

        # Already composed (set via Python, not yet saved)
        if hasattr(dt_val, '__class__') and dt_val.__class__ == self.field.whenever_type:
            return dt_val

        return self.compose(dt_val, meta_val)

    def __set__(self, instance: Any, value: Any) -> None:
        if value is None:
            instance.__dict__[self.attname] = None
            instance.__dict__[self.paired_attname] = None
            return

        if isinstance(value, self.field.whenever_type):
            dt_val, meta_val = self.decompose(value)
            instance.__dict__[self.attname] = value
            instance.__dict__[self.paired_attname] = meta_val
        else:
            # Raw assignment (e.g., from DB loading) — store as-is
            instance.__dict__[self.attname] = value
