"""Smoke tests for the NEXUS Streamlit application."""

from streamlit.testing.v1 import AppTest


def test_nexus_app_starts_without_exception():
    """Verify that the complete Streamlit application can start."""
    app = AppTest.from_file("app.py", default_timeout=30).run()

    assert not app.exception


def test_nexus_app_renders_core_interface():
    """Verify that the primary NEXUS interface is rendered."""
    app = AppTest.from_file("app.py", default_timeout=30).run()

    assert not app.exception
    assert len(app.sidebar) > 0
    assert len(app.button) > 0
