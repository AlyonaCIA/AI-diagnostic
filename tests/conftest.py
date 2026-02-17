"""
File: tests/conftest.py
Description: Shared pytest fixtures for the PLC diagnostic suite.
"""

# Load environment variables from .env file for tests
from dotenv import load_dotenv

load_dotenv()

import pytest

from app.utils.loader import load_fixture


@pytest.fixture
def constant_error_data():
    return {
        "log": load_fixture("constant_error.txt"),
        "xml": load_fixture("constant_error.xml"),
    }


@pytest.fixture
def empty_project_data():
    return {
        "log": load_fixture("empty_project.txt"),
        "xml": load_fixture("empty_project.xml"),
    }
