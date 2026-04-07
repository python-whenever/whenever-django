"""Tests for TimeDeltaField, ItemizedDeltaField, and ItemizedDateDeltaField."""

from __future__ import annotations

import datetime as stdlib_dt

import pytest
import whenever
from django.db import connection, models

from whenever_django.fields import (
    ItemizedDateDeltaField,
    ItemizedDeltaField,
    TimeDeltaField,
)

pytestmark = pytest.mark.django_db(transaction=True)

# ---------------------------------------------------------------------------
# Test model
# ---------------------------------------------------------------------------


class DeltaFieldModel(models.Model):
    time_delta = TimeDeltaField(null=True)
    time_delta_coerce = TimeDeltaField(null=True, from_stdlib=True)
    itemized_delta = ItemizedDeltaField(null=True)
    itemized_date_delta = ItemizedDateDeltaField(null=True)

    class Meta:
        app_label = "tests"


@pytest.fixture(autouse=True)
def _create_table():
    with connection.schema_editor() as editor:
        editor.create_model(DeltaFieldModel)
    yield
    with connection.schema_editor() as editor:
        editor.delete_model(DeltaFieldModel)


# ===================================================================
# TimeDeltaField
# ===================================================================


class TestTimeDeltaField:
    def test_null_roundtrip(self):
        obj = DeltaFieldModel.objects.create(time_delta=None)
        obj.refresh_from_db()
        assert obj.time_delta is None

    def test_basic_roundtrip(self):
        val = whenever.TimeDelta(hours=2, minutes=30)
        obj = DeltaFieldModel.objects.create(time_delta=val)
        obj.refresh_from_db()
        assert obj.time_delta == val

    def test_type_rejection(self):
        with pytest.raises(TypeError, match="TimeDeltaField expects TimeDelta"):
            DeltaFieldModel.objects.create(time_delta=stdlib_dt.timedelta(hours=2))

    def test_to_python_from_string(self):
        field = TimeDeltaField()
        result = field.to_python("PT2H30M")
        assert isinstance(result, whenever.TimeDelta)
        assert result == whenever.TimeDelta(hours=2, minutes=30)

    def test_deconstruct(self):
        field = TimeDeltaField()
        _, path, _, kwargs = field.deconstruct()
        assert path == "whenever_django.fields.time_delta.TimeDeltaField"
        assert "from_stdlib" not in kwargs

    def test_from_stdlib_coercion(self):
        stdlib_val = stdlib_dt.timedelta(hours=2, minutes=30)
        obj = DeltaFieldModel.objects.create(time_delta_coerce=stdlib_val)
        obj.refresh_from_db()
        assert isinstance(obj.time_delta_coerce, whenever.TimeDelta)
        assert obj.time_delta_coerce == whenever.TimeDelta(stdlib_val)

    def test_nanosecond_truncation(self):
        val = whenever.TimeDelta(hours=1, nanoseconds=123_456_789)
        obj = DeltaFieldModel.objects.create(time_delta=val)
        obj.refresh_from_db()
        # Microsecond precision only: 123_456 microseconds preserved, 789 nanoseconds lost
        expected = whenever.TimeDelta(hours=1, microseconds=123_456)
        assert obj.time_delta == expected


# ===================================================================
# ItemizedDeltaField
# ===================================================================


class TestItemizedDeltaField:
    def test_null_roundtrip(self):
        obj = DeltaFieldModel.objects.create(itemized_delta=None)
        obj.refresh_from_db()
        assert obj.itemized_delta is None

    def test_basic_roundtrip(self):
        val = whenever.ItemizedDelta(
            years=1, months=2, weeks=1, days=3, hours=4, minutes=30, seconds=15
        )
        obj = DeltaFieldModel.objects.create(itemized_delta=val)
        obj.refresh_from_db()
        assert obj.itemized_delta == val

    def test_type_rejection(self):
        with pytest.raises(TypeError, match="ItemizedDeltaField expects ItemizedDelta"):
            DeltaFieldModel.objects.create(itemized_delta=stdlib_dt.timedelta(hours=2))

    def test_to_python_from_string(self):
        field = ItemizedDeltaField()
        result = field.to_python("P1M15DT2H")
        assert isinstance(result, whenever.ItemizedDelta)

    def test_deconstruct(self):
        field = ItemizedDeltaField()
        _, path, _, kwargs = field.deconstruct()
        assert path == "whenever_django.fields.itemized_delta.ItemizedDeltaField"
        assert "from_stdlib" not in kwargs

    def test_from_stdlib_not_supported(self):
        with pytest.raises(TypeError, match="does not support from_stdlib"):
            ItemizedDeltaField(from_stdlib=True)

    def test_sparse_roundtrip(self):
        val = whenever.ItemizedDelta(hours=2)
        obj = DeltaFieldModel.objects.create(itemized_delta=val)
        obj.refresh_from_db()
        assert obj.itemized_delta == val
        # Verify sparseness: only non-zero keys stored
        sparse_dict = dict(val)
        assert "years" not in sparse_dict
        assert "months" not in sparse_dict


# ===================================================================
# ItemizedDateDeltaField
# ===================================================================


class TestItemizedDateDeltaField:
    def test_null_roundtrip(self):
        obj = DeltaFieldModel.objects.create(itemized_date_delta=None)
        obj.refresh_from_db()
        assert obj.itemized_date_delta is None

    def test_basic_roundtrip(self):
        val = whenever.ItemizedDateDelta(years=1, months=6)
        obj = DeltaFieldModel.objects.create(itemized_date_delta=val)
        obj.refresh_from_db()
        assert obj.itemized_date_delta == val

    def test_type_rejection(self):
        with pytest.raises(
            TypeError, match="ItemizedDateDeltaField expects ItemizedDateDelta"
        ):
            DeltaFieldModel.objects.create(
                itemized_date_delta=stdlib_dt.timedelta(days=30)
            )

    def test_to_python_from_string(self):
        field = ItemizedDateDeltaField()
        result = field.to_python("P1Y2M")
        assert isinstance(result, whenever.ItemizedDateDelta)

    def test_deconstruct(self):
        field = ItemizedDateDeltaField()
        _, path, _, kwargs = field.deconstruct()
        assert (
            path == "whenever_django.fields.itemized_date_delta.ItemizedDateDeltaField"
        )
        assert "from_stdlib" not in kwargs

    def test_from_stdlib_not_supported(self):
        with pytest.raises(TypeError, match="does not support from_stdlib"):
            ItemizedDateDeltaField(from_stdlib=True)

    def test_all_components_roundtrip(self):
        val = whenever.ItemizedDateDelta(years=2, months=3, weeks=1, days=5)
        obj = DeltaFieldModel.objects.create(itemized_date_delta=val)
        obj.refresh_from_db()
        assert obj.itemized_date_delta == val
