from __future__ import annotations

from typing import Any

import whenever
from rest_framework import serializers


class _WheneverSerializerField(serializers.Field):
    """Base for all whenever serializer fields.

    Subclasses only need to set ``whenever_type`` to the target
    :mod:`whenever` class; ``str()`` and ``parse_iso()`` handle the
    round-trip by convention.
    """

    whenever_type: type

    def to_representation(self, value: Any) -> str | None:
        if value is None:
            return None
        return str(value)

    def to_internal_value(self, data: Any) -> Any:
        if isinstance(data, self.whenever_type):
            return data
        try:
            return self.whenever_type.parse_iso(data)
        except (ValueError, TypeError) as exc:
            raise serializers.ValidationError(
                f"Invalid {self.whenever_type.__name__}: {exc}"
            ) from exc


class InstantSerializerField(_WheneverSerializerField):
    whenever_type = whenever.Instant


class PlainDateTimeSerializerField(_WheneverSerializerField):
    whenever_type = whenever.PlainDateTime


class ZonedDateTimeSerializerField(_WheneverSerializerField):
    whenever_type = whenever.ZonedDateTime


class OffsetDateTimeSerializerField(_WheneverSerializerField):
    whenever_type = whenever.OffsetDateTime


class WheneverDateSerializerField(_WheneverSerializerField):
    whenever_type = whenever.Date


class WheneverTimeSerializerField(_WheneverSerializerField):
    whenever_type = whenever.Time


class YearMonthSerializerField(_WheneverSerializerField):
    whenever_type = whenever.YearMonth


class MonthDaySerializerField(_WheneverSerializerField):
    whenever_type = whenever.MonthDay


class TimeDeltaSerializerField(_WheneverSerializerField):
    whenever_type = whenever.TimeDelta


class ItemizedDeltaSerializerField(_WheneverSerializerField):
    whenever_type = whenever.ItemizedDelta


class ItemizedDateDeltaSerializerField(_WheneverSerializerField):
    whenever_type = whenever.ItemizedDateDelta


def register_field_mapping() -> None:
    """Wire model fields to their serializer counterparts in ModelSerializer."""
    from rest_framework.serializers import ModelSerializer

    from whenever_django.fields import (
        InstantField,
        ItemizedDateDeltaField,
        ItemizedDeltaField,
        MonthDayField,
        OffsetDateTimeField,
        PlainDateTimeField,
        TimeDeltaField,
        WheneverDateField,
        WheneverTimeField,
        YearMonthField,
        ZonedDateTimeField,
    )

    mapping: dict[type, type] = {
        InstantField: InstantSerializerField,
        PlainDateTimeField: PlainDateTimeSerializerField,
        ZonedDateTimeField: ZonedDateTimeSerializerField,
        OffsetDateTimeField: OffsetDateTimeSerializerField,
        WheneverDateField: WheneverDateSerializerField,
        WheneverTimeField: WheneverTimeSerializerField,
        YearMonthField: YearMonthSerializerField,
        MonthDayField: MonthDaySerializerField,
        TimeDeltaField: TimeDeltaSerializerField,
        ItemizedDeltaField: ItemizedDeltaSerializerField,
        ItemizedDateDeltaField: ItemizedDateDeltaSerializerField,
    }
    ModelSerializer.serializer_field_mapping.update(mapping)


__all__ = [
    "InstantSerializerField",
    "PlainDateTimeSerializerField",
    "ZonedDateTimeSerializerField",
    "OffsetDateTimeSerializerField",
    "WheneverDateSerializerField",
    "WheneverTimeSerializerField",
    "YearMonthSerializerField",
    "MonthDaySerializerField",
    "TimeDeltaSerializerField",
    "ItemizedDeltaSerializerField",
    "ItemizedDateDeltaSerializerField",
]
