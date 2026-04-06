from __future__ import annotations

from typing import Any

_CACHE_PREFIX = "_whenever_"


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
        self.compose = compose
        self.decompose = decompose

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        if instance is None:
            return self

        cache_key = f"{_CACHE_PREFIX}{self.attname}"

        # Return cached whenever object if available
        cached = instance.__dict__.get(cache_key)
        if cached is not None:
            return cached

        # Deferred field check — Django's only()/defer() may exclude this
        # attribute from the initial query
        if self.attname not in instance.__dict__:
            instance.refresh_from_db(fields=[self.attname, self.paired_attname])

        dt_val = instance.__dict__.get(self.attname)
        if dt_val is None:
            return None

        if isinstance(dt_val, self.field.whenever_type):
            return dt_val

        meta_val = instance.__dict__.get(self.paired_attname)
        result = self.compose(dt_val, meta_val)
        if result is not None:
            instance.__dict__[cache_key] = result
        return result

    def __set__(self, instance: Any, value: Any) -> None:
        cache_key = f"{_CACHE_PREFIX}{self.attname}"

        if value is None:
            instance.__dict__[self.attname] = None
            instance.__dict__[self.paired_attname] = None
            instance.__dict__.pop(cache_key, None)
            return

        if isinstance(value, self.field.whenever_type):
            dt_value, meta_value = self.decompose(value)
            instance.__dict__[self.attname] = dt_value
            instance.__dict__[self.paired_attname] = meta_value
            instance.__dict__[cache_key] = value
        else:
            # During ORM hydration, Django assigns the raw DB value before
            # from_db_value runs, so we must accept non-whenever types here
            instance.__dict__[self.attname] = value
            instance.__dict__.pop(cache_key, None)
