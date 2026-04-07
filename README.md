# whenever-django

[![PyPI](https://img.shields.io/pypi/v/whenever-django.svg?color=blue)](https://pypi.python.org/pypi/whenever-django)
[![Python](https://img.shields.io/pypi/pyversions/whenever-django.svg)](https://pypi.python.org/pypi/whenever-django)
[![Django](https://img.shields.io/badge/django-%3E%3D4.2-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Django integration for the [whenever](https://github.com/ariebovenberg/whenever) datetime library.**

Stop crossing your fingers with `datetime`. Use type-safe, DST-aware temporal types in your Django models, forms, admin, DRF serializers, and ORM queries.

## Why?

Django's `DateTimeField` uses stdlib `datetime`, which [conflates naive and aware datetimes](https://dev.arie.bovenberg.net/blog/python-datetime-pitfalls/), silently drops timezone information on storage, and has no type-level enforcement. The `whenever` library fixes this with a strict one-type-per-use-case philosophy. **whenever-django** brings that strictness into the Django ecosystem:

- **Type safety** &mdash; `InstantField` only accepts `whenever.Instant`, never a stdlib `datetime`. Mistakes surface as `TypeError` at write time, not as silent data corruption.
- **Timezone preservation** &mdash; `ZonedDateTimeField` stores the IANA timezone in a paired column, so `America/New_York` survives the database round-trip.
- **Calendar-aware durations** &mdash; `ItemizedDeltaField` stores years, months, days, hours, etc. as separate components. Django's `DurationField` can only represent fixed `timedelta`.
- **Full ORM integration** &mdash; filter, annotate, and use F-expressions with whenever types natively.

## Installation

```bash
pip install whenever-django
```

With DRF support:

```bash
pip install whenever-django[drf]
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "whenever_django",
]
```

### Requirements

- Python 3.10+
- Django 4.2+
- [whenever](https://pypi.org/project/whenever/) 0.10.0+
- PostgreSQL or SQLite (MySQL is out of scope for v1)

## Quick Start

```python
import whenever
from django.db import models
from whenever_django.fields import InstantField, ZonedDateTimeField, WheneverDateField

class Event(models.Model):
    name = models.CharField(max_length=200)
    created_at = InstantField()
    starts_at = ZonedDateTimeField()
    date = WheneverDateField(null=True)

# Create
event = Event.objects.create(
    name="PyCon",
    created_at=whenever.Instant.now(),
    starts_at=whenever.ZonedDateTime(2026, 5, 15, 9, 0, tz="America/Chicago"),
    date=whenever.Date(2026, 5, 15),
)

# Query with whenever types
upcoming = Event.objects.filter(created_at__gte=whenever.Instant.now())

# The IANA timezone survives the round-trip
event.refresh_from_db()
assert event.starts_at.tz == "America/Chicago"
```

## Fields Reference

### Core Fields

| Field | whenever type | DB storage | stdlib equivalent |
|-------|--------------|------------|-------------------|
| `InstantField` | `Instant` | `TIMESTAMPTZ` / `TIMESTAMP` | `datetime` (aware, UTC) |
| `PlainDateTimeField` | `PlainDateTime` | `TIMESTAMP` (naive) | `datetime` (naive) |
| `WheneverDateField` | `Date` | `DATE` | `date` |
| `WheneverTimeField` | `Time` | `TIME` | `time` |

### Composite Fields

| Field | whenever type | DB storage |
|-------|--------------|------------|
| `ZonedDateTimeField` | `ZonedDateTime` | `TIMESTAMPTZ` + `VARCHAR` (IANA tz) |
| `OffsetDateTimeField` | `OffsetDateTime` | `TIMESTAMPTZ` + `VARCHAR` (UTC offset) |

Composite fields auto-manage a paired column (e.g., `starts_at_tz` for a `ZonedDateTimeField` named `starts_at`). One field declaration creates two database columns; migrations handle both automatically.

### Extended Types

| Field | whenever type | DB storage |
|-------|--------------|------------|
| `YearMonthField` | `YearMonth` | `INTEGER` (`YYYYMM`) |
| `MonthDayField` | `MonthDay` | `SMALLINT` (`MMDD`) |

### Delta Fields

| Field | whenever type | DB storage |
|-------|--------------|------------|
| `TimeDeltaField` | `TimeDelta` | `BIGINT` (microseconds) |
| `ItemizedDeltaField` | `ItemizedDelta` | `TEXT` (JSON) |
| `ItemizedDateDeltaField` | `ItemizedDateDelta` | `TEXT` (JSON) |

`TimeDeltaField` uses microsecond storage identical to Django's `DurationField`, enabling zero-downtime migration from existing `DurationField` columns.

## Field Options

### `from_stdlib`

All fields are **strict by default**: they reject stdlib types and raise `TypeError`. Set `from_stdlib=True` to enable automatic coercion from the corresponding stdlib type:

```python
class LegacyEvent(models.Model):
    # Accepts both whenever.Instant and datetime.datetime
    timestamp = InstantField(from_stdlib=True)
```

This is opt-in, not default &mdash; preserving whenever's type-safety philosophy. `from_stdlib` affects programmatic assignment and ORM writes; form fields and DRF serializers always parse from strings.

Fields without a stdlib equivalent (`YearMonthField`, `MonthDayField`, `ItemizedDeltaField`, `ItemizedDateDeltaField`) raise `TypeError` if `from_stdlib=True` is passed.

## Forms and Admin

Every model field provides a corresponding form field via `formfield()`. Fields render in Django admin without any custom `ModelAdmin` configuration:

```python
from whenever_django.forms.fields import InstantFormField, WheneverDateFormField

class EventForm(forms.Form):
    created_at = InstantFormField()  # Parses ISO 8601
    date = WheneverDateFormField()   # Parses YYYY-MM-DD
```

Form fields accept ISO 8601 strings and validate them into the correct whenever type.

## DRF Serializers

DRF integration is an **optional extra** (`pip install whenever-django[drf]`).

`ModelSerializer` auto-maps whenever model fields to their corresponding serializer fields with zero configuration:

```python
from rest_framework import serializers

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
    # InstantField -> InstantSerializerField (automatic)
    # ZonedDateTimeField -> ZonedDateTimeSerializerField (automatic)
```

Serialization formats:

| Field | Output format |
|-------|--------------|
| `InstantSerializerField` | `2026-04-06T10:00:00Z` |
| `PlainDateTimeSerializerField` | `2026-04-06T10:00:00` |
| `ZonedDateTimeSerializerField` | `2026-04-06T10:00:00-05:00[America/Chicago]` (RFC 9557) |
| `OffsetDateTimeSerializerField` | `2026-04-06T10:00:00-05:00` |
| `WheneverDateSerializerField` | `2026-04-06` |
| `WheneverTimeSerializerField` | `10:00:00` |
| `YearMonthSerializerField` | `2026-04` |
| `MonthDaySerializerField` | `04-06` |
| Delta fields | ISO 8601 duration |

Deserialization is strict: ambiguous input (e.g., a datetime string without offset for `InstantSerializerField`) is rejected.

## ORM Queries

### Lookups

Standard comparison lookups work with whenever types:

```python
from whenever import Instant, Date

Event.objects.filter(created_at__gte=Instant.now())
Event.objects.filter(date__range=(Date(2026, 1, 1), Date(2026, 12, 31)))
Event.objects.filter(created_at__in=[instant_a, instant_b])
```

Supported lookups: `exact`, `gt`, `gte`, `lt`, `lte`, `range`, `in`, `isnull`.

### Transforms

```python
Event.objects.filter(created_at__date=Date(2026, 4, 6))
Event.objects.filter(created_at__time__gte=Time(9, 0))
```

### Database Functions

```python
from whenever_django.functions import WheneverNow

Event.objects.filter(created_at__lte=WheneverNow())
```

## Migration Audit

The `whenever_audit` management command scans your models for stdlib datetime fields and recommends whenever replacements:

```bash
python manage.py whenever_audit
python manage.py whenever_audit --app-label myapp
```

Output:

```
whenever-django Migration Audit Report
==================================================
  myapp.Event.created_at: DateTimeField -> InstantField (or PlainDateTimeField for naive)
  myapp.Event.date: DateField -> WheneverDateField
  myapp.Event.duration: DurationField -> TimeDeltaField

Found 3 field(s) that can be converted.
```

## Known Limitations

1. **Composite field rename**: `RenameField` on `ZonedDateTimeField` / `OffsetDateTimeField` does not auto-rename the paired column. Workaround: manually add a second `RenameField` in the migration for the `_tz` / `_offset` column.

2. **Nanosecond precision**: All datetime fields truncate nanoseconds to microseconds on database storage (stdlib `datetime` limitation).

3. **SQLite limitations**: The `__in_tz` transform uses a Python-level function on SQLite instead of native `AT TIME ZONE`. Correct, but slower than PostgreSQL.

4. **`from_stdlib` scope**: The coercion option affects programmatic Python assignment only. Form fields and DRF serializers parse from strings regardless of this setting.

5. **JSON-stored deltas**: `ItemizedDeltaField` and `ItemizedDateDeltaField` use JSON storage, so they cannot participate in database-level arithmetic. F-expression arithmetic falls back to Python-level computation.

6. **MySQL not supported**: Only PostgreSQL and SQLite are supported in v1.

## Backend Support

| Feature | PostgreSQL | SQLite |
|---------|-----------|--------|
| All field types | Yes | Yes |
| Standard lookups | Yes | Yes |
| `__date` / `__time` transforms | Yes | Yes |
| `__in_tz` transform | Native `AT TIME ZONE` | Python fallback |
| `WheneverNow()` | Yes | Yes |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT &mdash; see [LICENSE](LICENSE).

## Related Projects

- [whenever](https://github.com/ariebovenberg/whenever) &mdash; The underlying datetime library
- [whenever-sqlalchemy](https://github.com/ariebovenberg/whenever-sqlalchemy) &mdash; SQLAlchemy integration for whenever
