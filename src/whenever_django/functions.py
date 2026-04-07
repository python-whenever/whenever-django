from __future__ import annotations

from django.db.models import Func

from whenever_django.fields import InstantField


class WheneverNow(Func):
    """Database-level current timestamp that returns an Instant."""

    template = "CURRENT_TIMESTAMP"

    @property
    def output_field(self) -> InstantField:
        return InstantField()


__all__ = ["WheneverNow"]
