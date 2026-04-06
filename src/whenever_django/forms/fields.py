from __future__ import annotations

from typing import Any

import whenever
from django import forms
from django.core.exceptions import ValidationError


class _WheneverFormField(forms.CharField):
    """Base form field that converts ISO 8601 strings to whenever types.

    Subclasses set ``whenever_type`` and ``type_label`` to control parsing
    and error messages.
    """

    whenever_type: type = None  # type: ignore[assignment]
    type_label: str = "value"

    def to_python(self, value: Any) -> Any:
        if not value:
            return None
        if isinstance(value, self.whenever_type):
            return value
        try:
            return self.whenever_type.parse_iso(str(value))
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Enter a valid ISO 8601 {self.type_label}: {e}"
            ) from e

    def prepare_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, self.whenever_type):
            return str(value)
        return super().prepare_value(value)


class InstantFormField(_WheneverFormField):
    whenever_type = whenever.Instant
    type_label = "instant"


class PlainDateTimeFormField(_WheneverFormField):
    whenever_type = whenever.PlainDateTime
    type_label = "datetime"


class WheneverDateFormField(_WheneverFormField):
    whenever_type = whenever.Date
    type_label = "date"


class WheneverTimeFormField(_WheneverFormField):
    whenever_type = whenever.Time
    type_label = "time"


class ZonedDateTimeFormField(_WheneverFormField):
    whenever_type = whenever.ZonedDateTime
    type_label = "zoned datetime (RFC 9557)"


class OffsetDateTimeFormField(_WheneverFormField):
    whenever_type = whenever.OffsetDateTime
    type_label = "offset datetime"


class YearMonthFormField(_WheneverFormField):
    whenever_type = whenever.YearMonth
    type_label = "year-month (YYYY-MM)"


class MonthDayFormField(_WheneverFormField):
    whenever_type = whenever.MonthDay
    type_label = "month-day (--MM-DD)"


class TimeDeltaFormField(_WheneverFormField):
    whenever_type = whenever.TimeDelta
    type_label = "duration (ISO 8601)"


class ItemizedDeltaFormField(_WheneverFormField):
    whenever_type = whenever.ItemizedDelta
    type_label = "itemized duration (ISO 8601)"


class ItemizedDateDeltaFormField(_WheneverFormField):
    whenever_type = whenever.ItemizedDateDelta
    type_label = "itemized date duration (ISO 8601)"
