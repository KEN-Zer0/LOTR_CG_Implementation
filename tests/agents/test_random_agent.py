import pytest

from agents.random_agent import RandomAgent
from src.cards import Ally, Enemy, Location
from config.limited.cards_list import Allies, Enemies, Locations, Sphere


@pytest.fixture
def agent():
    return RandomAgent()


@pytest.fixture
def enemy():
    return Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2)


# ── choose_questing_characters ─────────────────────────────────────────────

def test_questing_result_is_subset_of_available(agent, table):
    result = agent.choose_questing_characters(table, table.player_heroes)
    assert all(c in table.player_heroes for c in result)


def test_questing_empty_input_returns_empty(agent, table):
    assert agent.choose_questing_characters(table, []) == []


def test_questing_result_length_within_bounds(agent, table):
    result = agent.choose_questing_characters(table, table.player_heroes)
    assert 0 <= len(result) <= len(table.player_heroes)


# ── choose_card_to_play ────────────────────────────────────────────────────

def test_choose_card_returns_card_from_list_or_none(agent, table):
    cards = [Ally(Allies.Gondorian_Spearman, 1, 0, 2, 0, Sphere.Tactics, 2)]
    result = agent.choose_card_to_play(table, cards)
    assert result in cards or result is None


# ── choose_location ────────────────────────────────────────────────────────

def test_choose_location_returns_location_from_list_or_none(agent, table):
    loc = Location(Locations.Old_Forest_Road, 1, 2)
    result = agent.choose_location(table, [loc])
    assert result is loc or result is None


# ── choose_optional_engagement ─────────────────────────────────────────────

def test_optional_engagement_result_is_subset(agent, table, enemy):
    result = agent.choose_optional_engagement(table, [enemy])
    assert all(e is enemy for e in result)


def test_optional_engagement_empty_input_returns_empty(agent, table):
    assert agent.choose_optional_engagement(table, []) == []


# ── choose_defender ────────────────────────────────────────────────────────

def test_choose_defender_empty_available_returns_none(agent, table, enemy):
    assert agent.choose_defender(table, enemy, []) is None


def test_choose_defender_returns_character_from_pool_or_none(agent, table, enemy):
    result = agent.choose_defender(table, enemy, table.player_heroes)
    assert result in table.player_heroes or result is None


# ── choose_undefended_target ───────────────────────────────────────────────

def test_choose_undefended_target_returns_a_hero(agent, table, enemy):
    result = agent.choose_undefended_target(table, enemy)
    assert result in table.player_heroes


# ── choose_attackers ───────────────────────────────────────────────────────

def test_choose_attackers_empty_available_returns_empty(agent, table, enemy):
    assert agent.choose_attackers(table, enemy, []) == []


def test_choose_attackers_result_is_subset_of_available(agent, table, enemy):
    result = agent.choose_attackers(table, enemy, table.player_heroes)
    assert all(c in table.player_heroes for c in result)


def test_choose_attackers_length_within_bounds(agent, table, enemy):
    result = agent.choose_attackers(table, enemy, table.player_heroes)
    assert 0 <= len(result) <= len(table.player_heroes)
