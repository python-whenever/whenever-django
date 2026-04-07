"""Tests for the composite fields: ZonedDateTime and OffsetDateTime."""

from __future__ import annotations

import datetime as stdlib_dt

import pytest
import whenever
from django.db import connection, models

from whenever_django.fields import OffsetDateTimeField, ZonedDateTimeField

UTC = stdlib_dt.timezone.utc

pytestmark = pytest.mark.django_db(transaction=True)


class CompositeFieldModel(models.Model):
    zoned = ZonedDateTimeField(null=True)
    offset = OffsetDateTimeField(null=True)

    class Meta:
        app_label = "tests"


@pytest.fixture(autouse=True)
def _create_table():
    with connection.schema_editor() as editor:
        editor.create_model(CompositeFieldModel)
    yield
    with connection.schema_editor() as editor:
        editor.delete_model(CompositeFieldModel)


class TestZonedDateTimeField:
    def test_null_roundtrip(self):
        obj = CompositeFieldModel.objects.create(zoned=None)
        obj.refresh_from_db()
        assert obj.zoned is None

    def test_basic_roundtrip(self):
        val = whenever.ZonedDateTime(2026, 4, 6, 10, 0, 0, tz="America/New_York")
        obj = CompositeFieldModel.objects.create(zoned=val)
        obj.refresh_from_db()
        assert isinstance(obj.zoned, whenever.ZonedDateTime)
        assert obj.zoned == val
        assert obj.zoned.tz == "America/New_York"

    def test_timezone_preserved(self):
        val = whenever.ZonedDateTime(2026, 4, 6, 10, 0, 0, tz="Asia/Tokyo")
        obj = CompositeFieldModel.objects.create(zoned=val)
        obj.refresh_from_db()
        assert obj.zoned.tz == "Asia/Tokyo"
        # Verify it's not just storing UTC
        assert obj.zoned == val

    def test_type_rejection(self):
        with pytest.raises(TypeError, match="ZonedDateTimeField expects"):
            CompositeFieldModel.objects.create(zoned="not-a-zoned-datetime")

    def test_paired_column_exists(self):
        val = whenever.ZonedDateTime(2026, 4, 6, 10, 0, 0, tz="Europe/London")
        obj = CompositeFieldModel.objects.create(zoned=val)
        obj.refresh_from_db()
        # The paired column should be accessible on the instance
        assert obj.zoned_tz == "Europe/London"

    def test_to_python_from_string(self):
        field = ZonedDateTimeField()
        result = field.to_python("2026-04-06T10:00:00-04:00[America/New_York]")
        assert isinstance(result, whenever.ZonedDateTime)

    def test_to_python_none(self):
        field = ZonedDateTimeField()
        assert field.to_python(None) is None

    def test_deconstruct(self):
        field = ZonedDateTimeField()
        _, path, _, _ = field.deconstruct()
        assert path == "whenever_django.fields.zoned_datetime.ZonedDateTimeField"


class TestOffsetDateTimeField:
    def test_null_roundtrip(self):
        obj = CompositeFieldModel.objects.create(offset=None)
        obj.refresh_from_db()
        assert obj.offset is None

    def test_basic_roundtrip(self):
        val = whenever.OffsetDateTime(2026, 4, 6, 10, 0, 0, offset=whenever.hours(-4))
        obj = CompositeFieldModel.objects.create(offset=val)
        obj.refresh_from_db()
        assert isinstance(obj.offset, whenever.OffsetDateTime)
        assert obj.offset == val

    def test_offset_preserved(self):
        val = whenever.OffsetDateTime(2026, 4, 6, 10, 0, 0, offset=whenever.hours(9))
        obj = CompositeFieldModel.objects.create(offset=val)
        obj.refresh_from_db()
        assert obj.offset.offset == whenever.hours(9)

    def test_negative_offset(self):
        val = whenever.OffsetDateTime(
            2026,
            4,
            6,
            10,
            0,
            0,
            offset=whenever.hours(-5) + whenever.minutes(-30),
        )
        obj = CompositeFieldModel.objects.create(offset=val)
        obj.refresh_from_db()
        assert obj.offset == val
        assert obj.offset_offset == "-05:30"

    def test_type_rejection(self):
        with pytest.raises(TypeError, match="OffsetDateTimeField expects"):
            CompositeFieldModel.objects.create(offset="not-an-offset-datetime")

    def test_paired_column_exists(self):
        val = whenever.OffsetDateTime(2026, 4, 6, 10, 0, 0, offset=whenever.hours(-4))
        obj = CompositeFieldModel.objects.create(offset=val)
        obj.refresh_from_db()
        assert obj.offset_offset == "-04:00"

    def test_to_python_from_string(self):
        field = OffsetDateTimeField()
        result = field.to_python("2026-04-06T10:00:00-04:00")
        assert isinstance(result, whenever.OffsetDateTime)

    def test_deconstruct(self):
        field = OffsetDateTimeField()
        _, path, _, _ = field.deconstruct()
        assert path == "whenever_django.fields.offset_datetime.OffsetDateTimeField"
