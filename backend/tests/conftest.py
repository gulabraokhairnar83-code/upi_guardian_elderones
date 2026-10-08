import os
import sys

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app import create_app


@pytest.fixture
def app():
    """Create and configure a testing Flask application instance."""
    app = create_app("testing")
    return app


@pytest.fixture
def client(app):
    """A test client for the application."""
    return app.test_client()
