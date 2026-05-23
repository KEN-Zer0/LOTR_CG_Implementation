import pytest

from src.cards.progress_objective.location import Location


@pytest.fixture
def default_location():
    """Returns a fresh Location instance before each test."""
    return Location(name="Forest Clearing", threat=2, required_progress=4)


def test_location_initialization(default_location):
    # Check if all attributes and properties are set correctly
    assert default_location.name == "Forest Clearing"
    assert default_location.threat == 2
    assert default_location.required_progress == 4  # Inherited from ProgressObjective


def test_location_copy(default_location):
    # Create a copy of the location
    location_copy = default_location.copy()

    # Check if the copy is a different object in memory
    assert location_copy is not default_location

    # Check if all values were copied correctly
    assert location_copy.name == default_location.name
    assert location_copy.threat == default_location.threat
    assert location_copy.required_progress == default_location.required_progress