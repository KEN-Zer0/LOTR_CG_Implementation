import pytest

from agents.expert_agent import ExpertAgent
from config.limited.cards_registry import CARDS
from config.limited.cards_list import Allies, Enemies


@pytest.fixture
def agent():
    return ExpertAgent()


def test_commits_all_heroes(agent, table):
    result = agent.choose_questing_characters(table, table.player_heroes)
    assert result == table.player_heroes


def test_commits_all_allies(agent, table):
    allies = [CARDS[Allies.Gondorian_Spearman].copy(), CARDS[Allies.Wandering_Took].copy()]
    result = agent.choose_questing_characters(table, allies)
    assert result == allies


def test_commits_mixed_heroes_and_allies(agent, table):
    ally = CARDS[Allies.Lorien_Guide].copy()
    available = table.player_heroes + [ally]
    result = agent.choose_questing_characters(table, available)
    assert result == available


def test_empty_available_returns_empty(agent, table):
    assert agent.choose_questing_characters(table, []) == []


def test_single_character_returned(agent, table):
    single = [table.player_heroes[0]]
    assert agent.choose_questing_characters(table, single) == single
