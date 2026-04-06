"""Placeholder test for package structure."""


def test_package_imports() -> None:
    """Verify package can be imported."""
    import whenever_django

    assert hasattr(whenever_django, "__version__")
    assert whenever_django.__version__ == "0.0.1a0"
