import pytest

from src.cards.progress_objective.quest import Quest


@pytest.fixture
def default_quest():
    """Returns a fresh Quest instance before each test."""
    return Quest(
        name="Passage Through Mirkwood",
        scenario="Scenario 1",
        required_progress=8,
    )


def test_quest_initialization(default_quest):
    # Check if all attributes and properties are set correctly
    assert default_quest.name == "Passage Through Mirkwood"
    assert default_quest.scenario == "Scenario 1"
    assert default_quest.progress == 0  # Inherited from ProgressObjective


def test_quest_copy(default_quest):
    # Create a copy of the quest
    quest_copy = default_quest.copy()

    # Check if the copy is a different object in memory
    assert quest_copy is not default_quest

    # Check if all values were copied correctly
    assert quest_copy.name == default_quest.name
    assert quest_copy.scenario == default_quest.scenario
    assert (
        quest_copy._required_progress == default_quest._required_progress
    )  # From super().__init__