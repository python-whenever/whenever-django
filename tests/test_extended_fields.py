"""Tests for YearMonth and MonthDay fields."""
from __future__ import annotations

import pytest
import whenever
from django.db import connection, models

from whenever_django.fields import MonthDayField, YearMonthField


class ExtendedFieldModel(models.Model):
    year_month = YearMonthField(null=True)
    month_day = MonthDayField(null=True)

    class Meta:
        app_label = "tests"


@pytest.fixture(autouse=True)
def _create_table():
    with connection.schema_editor() as editor:
        editor.create_model(ExtendedFieldModel)
    yield
    with connection.schema_editor() as editor:
        editor.delete_model(ExtendedFieldModel)


class TestYearMonthField:
    def test_null_roundtrip(self):
        obj = ExtendedFieldModel.objects.create(year_month=None)
        obj.refresh_from_db()
        assert obj.year_month is None

    def test_basic_roundtrip(self):
        val = whenever.YearMonth(2026, 4)
        obj = ExtendedFieldModel.objects.create(year_month=val)
        obj.refresh_from_db()
        assert obj.year_month == val

    def test_type_rejection(self):
        with pytest.raises(TypeError, match="YearMonthField expects"):
            ExtendedFieldModel.objects.create(year_month="2026-04")

    def test_to_python_from_string(self):
        field = YearMonthField()
        result = field.to_python("2026-04")
        assert isinstance(result, whenever.YearMonth)
        assert result == whenever.YearMonth(2026, 4)

    def test_deconstruct(self):
        field = YearMonthField()
        _, path, _, _ = field.deconstruct()
        assert path == "whenever_django.fields.year_month.YearMonthField"

    def test_db_sorting(self):
        values = [
            whenever.YearMonth(2025, 12),
            whenever.YearMonth(2026, 1),
            whenever.YearMonth(2024, 6),
        ]
        for v in values:
            ExtendedFieldModel.objects.create(year_month=v)

        qs = ExtendedFieldModel.objects.filter(
            year_month__gte=whenever.YearMonth(2025, 12)
        ).order_by("year_month")
        results = [obj.year_month for obj in qs]
        assert results == [
            whenever.YearMonth(2025, 12),
            whenever.YearMonth(2026, 1),
        ]

    def test_from_stdlib_rejected(self):
        with pytest.raises(TypeError, match="does not support from_stdlib"):
            YearMonthField(from_stdlib=True)


class TestMonthDayField:
    def test_null_roundtrip(self):
        obj = ExtendedFieldModel.objects.create(month_day=None)
        obj.refresh_from_db()
        assert obj.month_day is None

    def test_basic_roundtrip(self):
        val = whenever.MonthDay(4, 6)
        obj = ExtendedFieldModel.objects.create(month_day=val)
        obj.refresh_from_db()
        assert obj.month_day == val

    def test_type_rejection(self):
        with pytest.raises(TypeError, match="MonthDayField expects"):
            ExtendedFieldModel.objects.create(month_day="--04-06")

    def test_to_python_from_string(self):
        field = MonthDayField()
        result = field.to_python("--04-06")
        assert isinstance(result, whenever.MonthDay)
        assert result == whenever.MonthDay(4, 6)

    def test_deconstruct(self):
        field = MonthDayField()
        _, path, _, _ = field.deconstruct()
        assert path == "whenever_django.fields.month_day.MonthDayField"

    def test_db_sorting(self):
        values = [
            whenever.MonthDay(12, 25),
            whenever.MonthDay(1, 5),
            whenever.MonthDay(4, 6),
        ]
        for v in values:
            ExtendedFieldModel.objects.create(month_day=v)

        qs = ExtendedFieldModel.objects.filter(
            month_day__gte=whenever.MonthDay(4, 6)
        ).order_by("month_day")
        results = [obj.month_day for obj in qs]
        assert results == [
            whenever.MonthDay(4, 6),
            whenever.MonthDay(12, 25),
        ]

    def test_from_stdlib_rejected(self):
        with pytest.raises(TypeError, match="does not support from_stdlib"):
            MonthDayField(from_stdlib=True)
