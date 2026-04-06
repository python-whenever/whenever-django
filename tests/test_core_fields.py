"""Tests for the four core whenever model fields."""
from __future__ import annotations

import datetime as stdlib_dt

import pytest
import whenever
from django.core.exceptions import ValidationError
from django.db import connection, models

from whenever_django.fields import (
    InstantField,
    PlainDateTimeField,
    WheneverDateField,
    WheneverTimeField,
)

UTC = stdlib_dt.timezone.utc


# ---------------------------------------------------------------------------
# Test models (created dynamically, no migration needed)
# ---------------------------------------------------------------------------


class CoreFieldModel(models.Model):
    instant = InstantField(null=True)
    instant_coerce = InstantField(null=True, from_stdlib=True)
    plain_dt = PlainDateTimeField(null=True)
    plain_dt_coerce = PlainDateTimeField(null=True, from_stdlib=True)
    date = WheneverDateField(null=True)
    date_coerce = WheneverDateField(null=True, from_stdlib=True)
    time = WheneverTimeField(null=True)
    time_coerce = WheneverTimeField(null=True, from_stdlib=True)

    class Meta:
        app_label = "tests"


@pytest.fixture(autouse=True)
def _create_table():
    with connection.schema_editor() as editor:
        editor.create_model(CoreFieldModel)
    yield
    with connection.schema_editor() as editor:
        editor.delete_model(CoreFieldModel)


# ===================================================================
# InstantField
# ===================================================================


class TestInstantField:
    def test_null_roundtrip(self):
        obj = CoreFieldModel.objects.create(instant=None)
        obj.refresh_from_db()
        assert obj.instant is None

    def test_basic_roundtrip(self):
        val = whenever.Instant.parse_iso("2026-04-06T10:00:00Z")
        obj = CoreFieldModel.objects.create(instant=val)
        obj.refresh_from_db()
        assert obj.instant == val

    def test_type_rejection(self):
        with pytest.raises(TypeError, match="InstantField expects Instant"):
            CoreFieldModel.objects.create(
                instant=stdlib_dt.datetime(2026, 4, 6, tzinfo=UTC)
            )

    def test_from_stdlib_coercion(self):
        stdlib_val = stdlib_dt.datetime(2026, 4, 6, 10, 0, 0, tzinfo=UTC)
        obj = CoreFieldModel.objects.create(instant_coerce=stdlib_val)
        obj.refresh_from_db()
        assert isinstance(obj.instant_coerce, whenever.Instant)
        assert obj.instant_coerce == whenever.Instant(stdlib_val)

    def test_from_db_restores_utc_for_naive(self):
        """SQLite drops tzinfo; from_db_value must restore UTC."""
        field = InstantField()
        naive = stdlib_dt.datetime(2026, 4, 6, 10, 0, 0)
        result = field.from_db_value(naive, None, None)
        assert isinstance(result, whenever.Instant)

    def test_to_python_idempotent(self):
        field = InstantField()
        val = whenever.Instant.parse_iso("2026-04-06T10:00:00Z")
        assert field.to_python(val) is val

    def test_to_python_from_string(self):
        field = InstantField()
        result = field.to_python("2026-04-06T10:00:00Z")
        assert isinstance(result, whenever.Instant)

    def test_to_python_none(self):
        field = InstantField()
        assert field.to_python(None) is None

    def test_to_python_invalid_string(self):
        field = InstantField()
        with pytest.raises(ValidationError):
            field.to_python("not-a-datetime")

    def test_deconstruct_default(self):
        field = InstantField()
        _, path, args, kwargs = field.deconstruct()
        assert path == "whenever_django.fields.instant.InstantField"
        assert "from_stdlib" not in kwargs

    def test_deconstruct_with_from_stdlib(self):
        field = InstantField(from_stdlib=True)
        _, _, _, kwargs = field.deconstruct()
        assert kwargs["from_stdlib"] is True

    def test_nanosecond_truncation(self):
        val = whenever.Instant.from_utc(2026, 4, 6, 10, 0, 0, nanosecond=123_456_789)
        obj = CoreFieldModel.objects.create(instant=val)
        obj.refresh_from_db()
        # Microseconds preserved, sub-microsecond lost
        expected = whenever.Instant.from_utc(
            2026, 4, 6, 10, 0, 0, nanosecond=123_456_000
        )
        assert obj.instant == expected

    def test_value_to_string(self):
        field = InstantField()
        field.attname = "instant"
        val = whenever.Instant.parse_iso("2026-04-06T10:00:00Z")
        obj = CoreFieldModel(instant=val)
        result = field.value_to_string(obj)
        assert result != ""


# ===================================================================
# PlainDateTimeField
# ===================================================================


class TestPlainDateTimeField:
    def test_null_roundtrip(self):
        obj = CoreFieldModel.objects.create(plain_dt=None)
        obj.refresh_from_db()
        assert obj.plain_dt is None

    def test_basic_roundtrip(self):
        val = whenever.PlainDateTime(2026, 4, 6, 10, 30, 0)
        obj = CoreFieldModel.objects.create(plain_dt=val)
        obj.refresh_from_db()
        assert obj.plain_dt == val

    def test_type_rejection(self):
        with pytest.raises(TypeError, match="PlainDateTimeField expects"):
            CoreFieldModel.objects.create(
                plain_dt=stdlib_dt.datetime(2026, 4, 6)
            )

    def test_from_stdlib_coercion_naive(self):
        stdlib_val = stdlib_dt.datetime(2026, 4, 6, 10, 30, 0)
        obj = CoreFieldModel.objects.create(plain_dt_coerce=stdlib_val)
        obj.refresh_from_db()
        assert isinstance(obj.plain_dt_coerce, whenever.PlainDateTime)

    def test_from_stdlib_rejects_aware(self):
        aware = stdlib_dt.datetime(2026, 4, 6, tzinfo=UTC)
        with pytest.raises(TypeError, match="does not accept aware"):
            CoreFieldModel.objects.create(plain_dt_coerce=aware)

    def test_to_python_from_string(self):
        field = PlainDateTimeField()
        result = field.to_python("2026-04-06T10:30:00")
        assert isinstance(result, whenever.PlainDateTime)

    def test_deconstruct(self):
        field = PlainDateTimeField()
        _, path, _, kwargs = field.deconstruct()
        assert path == "whenever_django.fields.plain_datetime.PlainDateTimeField"


# ===================================================================
# WheneverDateField
# ===================================================================


class TestWheneverDateField:
    def test_null_roundtrip(self):
        obj = CoreFieldModel.objects.create(date=None)
        obj.refresh_from_db()
        assert obj.date is None

    def test_basic_roundtrip(self):
        val = whenever.Date(2026, 4, 6)
        obj = CoreFieldModel.objects.create(date=val)
        obj.refresh_from_db()
        assert obj.date == val

    def test_type_rejection(self):
        with pytest.raises(TypeError, match="WheneverDateField expects"):
            CoreFieldModel.objects.create(
                date=stdlib_dt.date(2026, 4, 6)
            )

    def test_from_stdlib_coercion(self):
        stdlib_val = stdlib_dt.date(2026, 4, 6)
        obj = CoreFieldModel.objects.create(date_coerce=stdlib_val)
        obj.refresh_from_db()
        assert isinstance(obj.date_coerce, whenever.Date)
        assert obj.date_coerce == whenever.Date(2026, 4, 6)

    def test_to_python_from_string(self):
        field = WheneverDateField()
        result = field.to_python("2026-04-06")
        assert isinstance(result, whenever.Date)

    def test_deconstruct(self):
        field = WheneverDateField()
        _, path, _, _ = field.deconstruct()
        assert path == "whenever_django.fields.date.WheneverDateField"


# ===================================================================
# WheneverTimeField
# ===================================================================


class TestWheneverTimeField:
    def test_null_roundtrip(self):
        obj = CoreFieldModel.objects.create(time=None)
        obj.refresh_from_db()
        assert obj.time is None

    def test_basic_roundtrip(self):
        val = whenever.Time(10, 30, 45)
        obj = CoreFieldModel.objects.create(time=val)
        obj.refresh_from_db()
        assert obj.time == val

    def test_type_rejection(self):
        with pytest.raises(TypeError, match="WheneverTimeField expects"):
            CoreFieldModel.objects.create(
                time=stdlib_dt.time(10, 30, 45)
            )

    def test_from_stdlib_coercion(self):
        stdlib_val = stdlib_dt.time(10, 30, 45)
        obj = CoreFieldModel.objects.create(time_coerce=stdlib_val)
        obj.refresh_from_db()
        assert isinstance(obj.time_coerce, whenever.Time)
        assert obj.time_coerce == whenever.Time(10, 30, 45)

    def test_nanosecond_truncation(self):
        val = whenever.Time(10, 30, 45, nanosecond=123_456_789)
        obj = CoreFieldModel.objects.create(time=val)
        obj.refresh_from_db()
        expected = whenever.Time(10, 30, 45, nanosecond=123_456_000)
        assert obj.time == expected

    def test_to_python_from_string(self):
        field = WheneverTimeField()
        result = field.to_python("10:30:45")
        assert isinstance(result, whenever.Time)

    def test_deconstruct(self):
        field = WheneverTimeField()
        _, path, _, _ = field.deconstruct()
        assert path == "whenever_django.fields.time.WheneverTimeField"


# ===================================================================
# from_stdlib=True not allowed on fields without stdlib equivalents
# ===================================================================


class TestFromStdlibValidation:
    def test_base_field_rejects_from_stdlib_when_no_stdlib_type(self):
        from whenever_django.fields._base import WheneverField

        class NoStdlibField(WheneverField):
            whenever_type = whenever.Instant
            stdlib_type = None

            def _from_db(self, value, connection): ...
            def _to_db(self, value): ...
            def _parse(self, value): ...

        with pytest.raises(TypeError, match="does not support from_stdlib"):
            NoStdlibField(from_stdlib=True)
