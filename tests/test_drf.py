"""Tests for DRF serializer fields."""
from __future__ import annotations

import pytest

rest_framework = pytest.importorskip("rest_framework")

import whenever
from rest_framework import serializers

from whenever_django.contrib.drf.fields import (
    InstantSerializerField,
    ItemizedDateDeltaSerializerField,
    ItemizedDeltaSerializerField,
    MonthDaySerializerField,
    OffsetDateTimeSerializerField,
    PlainDateTimeSerializerField,
    TimeDeltaSerializerField,
    WheneverDateSerializerField,
    WheneverTimeSerializerField,
    YearMonthSerializerField,
    ZonedDateTimeSerializerField,
)

# ---------------------------------------------------------------------------
# Parametrized fixtures: (field_class, whenever_value, iso_string)
# ---------------------------------------------------------------------------

FIELD_CASES = [
    (
        InstantSerializerField,
        whenever.Instant.from_utc(2026, 4, 6, 10),
        "2026-04-06T10:00:00Z",
    ),
    (
        PlainDateTimeSerializerField,
        whenever.PlainDateTime(2026, 4, 6, 10),
        "2026-04-06T10:00:00",
    ),
    (
        ZonedDateTimeSerializerField,
        whenever.ZonedDateTime(2026, 4, 6, 10, tz="America/New_York"),
        "2026-04-06T10:00:00-04:00[America/New_York]",
    ),
    (
        OffsetDateTimeSerializerField,
        whenever.OffsetDateTime(2026, 4, 6, 10, offset=-4),
        "2026-04-06T10:00:00-04:00",
    ),
    (
        WheneverDateSerializerField,
        whenever.Date(2026, 4, 6),
        "2026-04-06",
    ),
    (
        WheneverTimeSerializerField,
        whenever.Time(10, 0, 0),
        "10:00:00",
    ),
    (
        YearMonthSerializerField,
        whenever.YearMonth(2026, 4),
        "2026-04",
    ),
    (
        MonthDaySerializerField,
        whenever.MonthDay(4, 6),
        "--04-06",
    ),
    (
        TimeDeltaSerializerField,
        whenever.TimeDelta(hours=2, minutes=30),
        "PT2H30M",
    ),
    (
        ItemizedDeltaSerializerField,
        whenever.ItemizedDelta(months=1, days=15, hours=2),
        "P1M15DT2H",
    ),
    (
        ItemizedDateDeltaSerializerField,
        whenever.ItemizedDateDelta(years=1, months=2, days=10),
        "P1Y2M10D",
    ),
]


@pytest.mark.parametrize(
    ("field_class", "value", "expected_str"),
    FIELD_CASES,
    ids=[c[0].__name__ for c in FIELD_CASES],
)
class TestSerializerFields:
    def test_to_representation(self, field_class, value, expected_str):
        field = field_class()
        assert field.to_representation(value) == expected_str

    def test_to_representation_none(self, field_class, value, expected_str):
        field = field_class()
        assert field.to_representation(None) is None

    def test_to_internal_value(self, field_class, value, expected_str):
        field = field_class()
        result = field.to_internal_value(expected_str)
        assert result == value

    def test_to_internal_value_passthrough(self, field_class, value, expected_str):
        """Already-parsed whenever objects pass through unchanged."""
        field = field_class()
        assert field.to_internal_value(value) == value

    def test_invalid_input(self, field_class, value, expected_str):
        field = field_class()
        with pytest.raises(serializers.ValidationError):
            field.to_internal_value("not-a-valid-value")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_register_serializer_fields():
    """Model field → serializer field mapping is installed on ModelSerializer."""
    from rest_framework.serializers import ModelSerializer

    from whenever_django.fields import InstantField

    assert InstantField in ModelSerializer.serializer_field_mapping
    assert (
        ModelSerializer.serializer_field_mapping[InstantField]
        is InstantSerializerField
    )
