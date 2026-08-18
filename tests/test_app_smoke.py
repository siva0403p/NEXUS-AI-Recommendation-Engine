"""Smoke tests for the NEXUS Streamlit application."""

from pathlib import Path
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


def test_nexus_app_starts_without_exception():
    """Verify that the complete Streamlit application can start."""
    app = AppTest.from_file(APP_PATH, default_timeout=30).run()

    assert not app.exception


def test_nexus_app_renders_core_interface():
    """Verify that the primary NEXUS interface is rendered."""
    app = AppTest.from_file(APP_PATH, default_timeout=30).run()

    assert not app.exception
    assert len(app.sidebar) > 0
    assert len(app.button) > 0
