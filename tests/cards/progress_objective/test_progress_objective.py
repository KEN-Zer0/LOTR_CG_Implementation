import pytest

from src.cards.progress_objective.progress_objective import ProgressObjective


@pytest.fixture
def default_objective():
    """Returns a fresh ProgressObjective instance before each test."""
    return ProgressObjective(name="Explore the Cave", required_progress=5)


def test_objective_initialization(default_objective):
    # Check attributes and starting progress after creation
    assert default_objective.name == "Explore the Cave"
    assert default_objective.progress == 0


def test_objective_is_not_complete_initially(default_objective):
    # New objective must not be complete
    assert default_objective.is_complete() is False


def test_place_progress_token(default_objective):
    # Add tokens and check current progress
    default_objective.place_progress_token(3)
    assert default_objective.progress == 3
    assert default_objective.is_complete() is False


def test_is_complete_exact(default_objective):
    # Add exact tokens needed to complete the objective
    default_objective.place_progress_token(5)
    assert default_objective.progress == 5
    assert default_objective.is_complete() is True


def test_is_complete_overflow(default_objective):
    # Add more tokens than required
    default_objective.place_progress_token(10)
    assert default_objective.progress == 10
    assert default_objective.is_complete() is True