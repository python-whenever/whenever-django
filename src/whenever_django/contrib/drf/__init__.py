from __future__ import annotations


def register_serializer_fields() -> None:
    """Register whenever serializer fields with DRF's ModelSerializer."""
    from .fields import register_field_mapping

    register_field_mapping()
