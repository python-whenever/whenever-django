"""Tests for whenever form fields and model field formfield() integration."""
from __future__ import annotations

import pytest
import whenever
from django.core.exceptions import ValidationError

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
from whenever_django.forms import (
    InstantFormField,
    ItemizedDateDeltaFormField,
    ItemizedDeltaFormField,
    MonthDayFormField,
    OffsetDateTimeFormField,
    PlainDateTimeFormField,
    TimeDeltaFormField,
    WheneverDateFormField,
    WheneverTimeFormField,
    YearMonthFormField,
    ZonedDateTimeFormField,
)


# ---------------------------------------------------------------------------
# Parametrized test data: (form_field_cls, model_field_cls, valid_iso, whenever_type, factory)
# ---------------------------------------------------------------------------

FIELD_CASES = [
    (
        InstantFormField,
        InstantField,
        "2026-04-06T10:00:00Z",
        whenever.Instant,
        lambda: whenever.Instant.parse_iso("2026-04-06T10:00:00Z"),
    ),
    (
        PlainDateTimeFormField,
        PlainDateTimeField,
        "2026-04-06T10:30:00",
        whenever.PlainDateTime,
        lambda: whenever.PlainDateTime(2026, 4, 6, 10, 30),
    ),
    (
        WheneverDateFormField,
        WheneverDateField,
        "2026-04-06",
        whenever.Date,
        lambda: whenever.Date(2026, 4, 6),
    ),
    (
        WheneverTimeFormField,
        WheneverTimeField,
        "10:30:45",
        whenever.Time,
        lambda: whenever.Time(10, 30, 45),
    ),
    (
        ZonedDateTimeFormField,
        ZonedDateTimeField,
        "2026-04-06T10:00:00-04:00[America/New_York]",
        whenever.ZonedDateTime,
        lambda: whenever.ZonedDateTime.parse_iso(
            "2026-04-06T10:00:00-04:00[America/New_York]"
        ),
    ),
    (
        OffsetDateTimeFormField,
        OffsetDateTimeField,
        "2026-04-06T10:00:00-04:00",
        whenever.OffsetDateTime,
        lambda: whenever.OffsetDateTime.parse_iso("2026-04-06T10:00:00-04:00"),
    ),
    (
        YearMonthFormField,
        YearMonthField,
        "2026-04",
        whenever.YearMonth,
        lambda: whenever.YearMonth(2026, 4),
    ),
    (
        MonthDayFormField,
        MonthDayField,
        "--04-06",
        whenever.MonthDay,
        lambda: whenever.MonthDay(4, 6),
    ),
    (
        TimeDeltaFormField,
        TimeDeltaField,
        "PT2H30M",
        whenever.TimeDelta,
        lambda: whenever.TimeDelta(hours=2, minutes=30),
    ),
    (
        ItemizedDeltaFormField,
        ItemizedDeltaField,
        "PT2H30M",
        whenever.ItemizedDelta,
        lambda: whenever.ItemizedDelta(hours=2, minutes=30),
    ),
    (
        ItemizedDateDeltaFormField,
        ItemizedDateDeltaField,
        "P1Y2M",
        whenever.ItemizedDateDelta,
        lambda: whenever.ItemizedDateDelta(years=1, months=2),
    ),
]


def _id(case: tuple) -> str:
    return case[0].__name__


@pytest.mark.parametrize(
    "form_field_cls, model_field_cls, valid_iso, whenever_type, factory",
    FIELD_CASES,
    ids=[c[0].__name__ for c in FIELD_CASES],
)
class TestFormFields:
    def test_valid_input(
        self, form_field_cls, model_field_cls, valid_iso, whenever_type, factory
    ):
        field = form_field_cls()
        result = field.to_python(valid_iso)
        assert isinstance(result, whenever_type)

    def test_invalid_input(
        self, form_field_cls, model_field_cls, valid_iso, whenever_type, factory
    ):
        field = form_field_cls()
        with pytest.raises(ValidationError):
            field.to_python("not-valid-at-all")

    def test_empty_input_none(
        self, form_field_cls, model_field_cls, valid_iso, whenever_type, factory
    ):
        field = form_field_cls()
        assert field.to_python("") is None

    def test_empty_input_none_value(
        self, form_field_cls, model_field_cls, valid_iso, whenever_type, factory
    ):
        field = form_field_cls()
        assert field.to_python(None) is None

    def test_prepare_value_from_whenever_type(
        self, form_field_cls, model_field_cls, valid_iso, whenever_type, factory
    ):
        field = form_field_cls()
        value = factory()
        rendered = field.prepare_value(value)
        assert isinstance(rendered, str)
        assert len(rendered) > 0

    def test_prepare_value_none(
        self, form_field_cls, model_field_cls, valid_iso, whenever_type, factory
    ):
        field = form_field_cls()
        assert field.prepare_value(None) == ""

    def test_prepare_value_roundtrip(
        self, form_field_cls, model_field_cls, valid_iso, whenever_type, factory
    ):
        """prepare_value output should be parseable back by to_python."""
        field = form_field_cls()
        value = factory()
        rendered = field.prepare_value(value)
        reparsed = field.to_python(rendered)
        assert isinstance(reparsed, whenever_type)

    def test_idempotent_to_python(
        self, form_field_cls, model_field_cls, valid_iso, whenever_type, factory
    ):
        """Passing an already-parsed whenever type through to_python returns it unchanged."""
        field = form_field_cls()
        value = factory()
        assert field.to_python(value) is value

    def test_formfield_integration(
        self, form_field_cls, model_field_cls, valid_iso, whenever_type, factory
    ):
        model_field = model_field_cls()
        form_field = model_field.formfield()
        assert isinstance(form_field, form_field_cls)
