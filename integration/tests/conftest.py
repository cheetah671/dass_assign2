"""Pytest fixtures for StreetRace Manager integration tests."""

import os
import sys

import pytest

CODE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code"))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from streetrace_manager import StreetRaceManager  # noqa: E402


@pytest.fixture
def app():
    """Return a clean app instance for each test."""
    instance = StreetRaceManager(initial_cash=500)
    instance.inventory.add_car("CAR-1", "Skyline")
    instance.inventory.add_car("CAR-2", "Supra")
    instance.inventory.add_spare_parts(5)
    instance.inventory.add_tools(2)
    return instance
