from __future__ import annotations


def _has_rest_framework() -> bool:
    try:
        import rest_framework  # noqa: F401

        return True
    except ImportError:
        return False


HAS_REST_FRAMEWORK = _has_rest_framework()
