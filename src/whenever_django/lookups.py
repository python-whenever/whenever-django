from __future__ import annotations

from typing import Any

from django.db.models import Transform

from whenever_django.fields import (
    InstantField,
    PlainDateTimeField,
    WheneverDateField,
    WheneverTimeField,
)


class DateTransform(Transform):
    """Extract the date portion from a datetime column."""

    lookup_name = "date"

    @property
    def output_field(self) -> WheneverDateField:
        return WheneverDateField()

    def as_sql(
        self, compiler: Any, connection: Any
    ) -> tuple[str, list[Any]]:
        lhs, params = compiler.compile(self.lhs)
        return f"DATE({lhs})", params


class TimeTransform(Transform):
    """Extract the time portion from a datetime column."""

    lookup_name = "time"

    @property
    def output_field(self) -> WheneverTimeField:
        return WheneverTimeField()

    def as_sql(
        self, compiler: Any, connection: Any
    ) -> tuple[str, list[Any]]:
        lhs, params = compiler.compile(self.lhs)
        return f"TIME({lhs})", params


def register_lookups() -> None:
    """Register transforms on datetime-like fields.

    Standard lookups (exact, gt, gte, lt, lte, range, in) already work
    because Django's query compilation calls get_prep_value() on the field.
    We only need to register custom transforms that extract sub-components.
    """
    InstantField.register_lookup(DateTransform)
    InstantField.register_lookup(TimeTransform)
    PlainDateTimeField.register_lookup(DateTransform)
    PlainDateTimeField.register_lookup(TimeTransform)
