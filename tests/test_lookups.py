"""Tests for ORM lookups, transforms, and database functions."""

from __future__ import annotations

import datetime as stdlib_dt

import pytest
import whenever
from django.db import connection, models

from whenever_django.fields import (
    InstantField,
    MonthDayField,
    WheneverDateField,
    WheneverTimeField,
    YearMonthField,
)
from whenever_django.functions import WheneverNow

UTC = stdlib_dt.timezone.utc

pytestmark = pytest.mark.django_db(transaction=True)


class LookupTestModel(models.Model):
    instant = InstantField(null=True)
    date = WheneverDateField(null=True)
    time = WheneverTimeField(null=True)
    year_month = YearMonthField(null=True)
    month_day = MonthDayField(null=True)

    class Meta:
        app_label = "tests"


@pytest.fixture(autouse=True)
def _create_table():
    with connection.schema_editor() as editor:
        editor.create_model(LookupTestModel)
    yield
    with connection.schema_editor() as editor:
        editor.delete_model(LookupTestModel)


# ---------------------------------------------------------------------------
# Standard lookups
# ---------------------------------------------------------------------------


class TestExactLookup:
    def test_instant_exact(self):
        val = whenever.Instant.parse_iso("2026-04-06T10:00:00Z")
        obj = LookupTestModel.objects.create(instant=val)
        result = LookupTestModel.objects.filter(instant=val)
        assert list(result) == [obj]

    def test_date_exact(self):
        val = whenever.Date(2026, 4, 6)
        obj = LookupTestModel.objects.create(date=val)
        result = LookupTestModel.objects.filter(date=val)
        assert list(result) == [obj]

    def test_time_exact(self):
        val = whenever.Time(10, 30, 0)
        obj = LookupTestModel.objects.create(time=val)
        result = LookupTestModel.objects.filter(time=val)
        assert list(result) == [obj]

    def test_year_month_exact(self):
        val = whenever.YearMonth(2026, 4)
        obj = LookupTestModel.objects.create(year_month=val)
        result = LookupTestModel.objects.filter(year_month=val)
        assert list(result) == [obj]

    def test_month_day_exact(self):
        val = whenever.MonthDay(4, 6)
        obj = LookupTestModel.objects.create(month_day=val)
        result = LookupTestModel.objects.filter(month_day=val)
        assert list(result) == [obj]

    def test_exact_no_match(self):
        LookupTestModel.objects.create(
            instant=whenever.Instant.parse_iso("2026-04-06T10:00:00Z")
        )
        other = whenever.Instant.parse_iso("2025-01-01T00:00:00Z")
        assert not LookupTestModel.objects.filter(instant=other).exists()


class TestComparisonLookups:
    def test_instant_gte(self):
        early = whenever.Instant.parse_iso("2026-01-01T00:00:00Z")
        late = whenever.Instant.parse_iso("2026-12-31T23:59:59Z")
        LookupTestModel.objects.create(instant=early)
        obj_late = LookupTestModel.objects.create(instant=late)

        cutoff = whenever.Instant.parse_iso("2026-06-01T00:00:00Z")
        result = LookupTestModel.objects.filter(instant__gte=cutoff)
        assert list(result) == [obj_late]

    def test_date_lt(self):
        d1 = whenever.Date(2026, 1, 1)
        d2 = whenever.Date(2026, 12, 31)
        obj_early = LookupTestModel.objects.create(date=d1)
        LookupTestModel.objects.create(date=d2)

        result = LookupTestModel.objects.filter(date__lt=whenever.Date(2026, 6, 1))
        assert list(result) == [obj_early]

    def test_year_month_gt(self):
        ym1 = whenever.YearMonth(2026, 1)
        ym2 = whenever.YearMonth(2026, 12)
        LookupTestModel.objects.create(year_month=ym1)
        obj2 = LookupTestModel.objects.create(year_month=ym2)

        result = LookupTestModel.objects.filter(
            year_month__gt=whenever.YearMonth(2026, 6)
        )
        assert list(result) == [obj2]

    def test_month_day_lte(self):
        md1 = whenever.MonthDay(1, 15)
        md2 = whenever.MonthDay(12, 25)
        obj1 = LookupTestModel.objects.create(month_day=md1)
        LookupTestModel.objects.create(month_day=md2)

        result = LookupTestModel.objects.filter(month_day__lte=whenever.MonthDay(6, 1))
        assert list(result) == [obj1]


class TestRangeLookup:
    def test_year_month_range(self):
        ym_jan = whenever.YearMonth(2026, 1)
        ym_jun = whenever.YearMonth(2026, 6)
        ym_dec = whenever.YearMonth(2026, 12)

        obj_jan = LookupTestModel.objects.create(year_month=ym_jan)
        obj_jun = LookupTestModel.objects.create(year_month=ym_jun)
        LookupTestModel.objects.create(year_month=ym_dec)

        result = LookupTestModel.objects.filter(year_month__range=(ym_jan, ym_jun))
        assert set(result) == {obj_jan, obj_jun}

    def test_instant_range(self):
        start = whenever.Instant.parse_iso("2026-03-01T00:00:00Z")
        mid = whenever.Instant.parse_iso("2026-06-01T00:00:00Z")
        end = whenever.Instant.parse_iso("2026-09-01T00:00:00Z")

        LookupTestModel.objects.create(
            instant=whenever.Instant.parse_iso("2026-01-01T00:00:00Z")
        )
        obj_mid = LookupTestModel.objects.create(instant=mid)
        LookupTestModel.objects.create(
            instant=whenever.Instant.parse_iso("2026-12-01T00:00:00Z")
        )

        result = LookupTestModel.objects.filter(instant__range=(start, end))
        assert list(result) == [obj_mid]


class TestInLookup:
    def test_date_in(self):
        d1 = whenever.Date(2026, 1, 1)
        d2 = whenever.Date(2026, 6, 15)
        d3 = whenever.Date(2026, 12, 31)

        obj1 = LookupTestModel.objects.create(date=d1)
        LookupTestModel.objects.create(date=d2)
        obj3 = LookupTestModel.objects.create(date=d3)

        result = LookupTestModel.objects.filter(date__in=[d1, d3])
        assert set(result) == {obj1, obj3}


# ---------------------------------------------------------------------------
# Transforms
# ---------------------------------------------------------------------------


class TestDateTransform:
    def test_instant_date_transform(self):
        val = whenever.Instant.parse_iso("2026-04-06T10:30:00Z")
        obj = LookupTestModel.objects.create(instant=val)

        result = LookupTestModel.objects.filter(instant__date=whenever.Date(2026, 4, 6))
        assert list(result) == [obj]

    def test_instant_date_transform_no_match(self):
        LookupTestModel.objects.create(
            instant=whenever.Instant.parse_iso("2026-04-06T10:30:00Z")
        )
        result = LookupTestModel.objects.filter(instant__date=whenever.Date(2026, 4, 7))
        assert not result.exists()


class TestTimeTransform:
    def test_instant_time_transform(self):
        val = whenever.Instant.parse_iso("2026-04-06T10:30:00Z")
        obj = LookupTestModel.objects.create(instant=val)

        result = LookupTestModel.objects.filter(instant__time=whenever.Time(10, 30, 0))
        assert list(result) == [obj]


# ---------------------------------------------------------------------------
# Database functions
# ---------------------------------------------------------------------------


class TestWheneverNow:
    def test_whenever_now_returns_instant(self):
        LookupTestModel.objects.create(
            instant=whenever.Instant.parse_iso("2026-04-06T10:00:00Z")
        )
        row = LookupTestModel.objects.annotate(now=WheneverNow()).first()
        assert isinstance(row.now, whenever.Instant)

    def test_whenever_now_is_recent(self):
        """Sanity check: DB timestamp is within a reasonable window."""
        LookupTestModel.objects.create(
            instant=whenever.Instant.parse_iso("2026-04-06T10:00:00Z")
        )
        row = LookupTestModel.objects.annotate(now=WheneverNow()).first()
        stdlib_now = row.now.to_stdlib()
        assert abs((stdlib_now - stdlib_dt.datetime.now(tz=UTC)).total_seconds()) < 5
