from __future__ import annotations

from django.db.models import Func

from whenever_django.fields import InstantField


class WheneverNow(Func):  # type: ignore[misc]
    """Database-level current timestamp that returns an Instant."""

    template = "CURRENT_TIMESTAMP"
    output_field = InstantField()
