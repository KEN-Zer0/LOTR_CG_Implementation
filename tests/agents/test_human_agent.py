import pytest

from agents.human_agent import HumanAgent
from src.cards import Ally, Enemy, Location
from config.limited.cards_list import Allies, Enemies, Locations, Sphere


@pytest.fixture
def agent():
    return HumanAgent()


@pytest.fixture
def enemy():
    return Enemy(Enemies.Dol_Guldur_Orcs, attack=2, defense=0, max_hit_points=3, engagement=10, threat=2)


# ── choose_questing_characters ─────────────────────────────────────────────

def test_questing_empty_available_returns_empty(agent, table):
    assert agent.choose_questing_characters(table, []) == []


def test_questing_blank_input_returns_empty(agent, table, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    result = agent.choose_questing_characters(table, table.player_heroes)
    assert result == []


def test_questing_single_selection(agent, table, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1")
    result = agent.choose_questing_characters(table, table.player_heroes)
    assert result == [table.player_heroes[0]]


def test_questing_multi_selection(agent, table, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1,3")
    result = agent.choose_questing_characters(table, table.player_heroes)
    assert result == [table.player_heroes[0], table.player_heroes[2]]


def test_questing_invalid_then_valid(agent, table, monkeypatch):
    responses = iter(["99", "1"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    result = agent.choose_questing_characters(table, table.player_heroes)
    assert result == [table.player_heroes[0]]


def test_questing_result_is_subset_of_available(agent, table, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "2")
    result = agent.choose_questing_characters(table, table.player_heroes)
    assert all(c in table.player_heroes for c in result)


# ── choose_card_to_play ────────────────────────────────────────────────────

def test_choose_card_zero_returns_none(agent, table, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "0")
    card = Ally(Allies.Gondorian_Spearman, attack=1, defense=1, max_hit_points=1, willpower=0, sphere_of_influence=Sphere.Tactics, cost=2)
    assert agent.choose_card_to_play(table, [card]) is None


def test_choose_card_blank_returns_none(agent, table, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    card = Ally(Allies.Gondorian_Spearman, attack=1, defense=1, max_hit_points=1, willpower=0, sphere_of_influence=Sphere.Tactics, cost=2)
    assert agent.choose_card_to_play(table, [card]) is None


def test_choose_card_selects_card(agent, table, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1")
    card = Ally(Allies.Gondorian_Spearman, attack=1, defense=1, max_hit_points=1, willpower=0, sphere_of_influence=Sphere.Tactics, cost=2)
    assert agent.choose_card_to_play(table, [card]) is card


def test_choose_card_empty_list_returns_none(agent, table):
    assert agent.choose_card_to_play(table, []) is None


# ── choose_location ────────────────────────────────────────────────────────

def test_choose_location_zero_returns_none(agent, table, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "0")
    loc = Location(Locations.Old_Forest_Road, threat=1, required_progress=3)
    assert agent.choose_location(table, [loc]) is None


def test_choose_location_selects_location(agent, table, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1")
    loc = Location(Locations.Old_Forest_Road, threat=1, required_progress=3)
    assert agent.choose_location(table, [loc]) is loc


def test_choose_location_empty_list_returns_none(agent, table):
    assert agent.choose_location(table, []) is None


# ── choose_optional_engagement ─────────────────────────────────────────────

def test_optional_engagement_blank_returns_empty(agent, table, enemy, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    assert agent.choose_optional_engagement(table, [enemy]) == []


def test_optional_engagement_selects_enemy(agent, table, enemy, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1")
    result = agent.choose_optional_engagement(table, [enemy])
    assert result == [enemy]


def test_optional_engagement_empty_available_returns_empty(agent, table):
    assert agent.choose_optional_engagement(table, []) == []


# ── choose_defender ────────────────────────────────────────────────────────

def test_choose_defender_zero_returns_none(agent, table, enemy, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "0")
    assert agent.choose_defender(table, enemy, table.player_heroes) is None


def test_choose_defender_selects_character(agent, table, enemy, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1")
    result = agent.choose_defender(table, enemy, table.player_heroes)
    assert result is table.player_heroes[0]


def test_choose_defender_empty_available_returns_none(agent, table, enemy):
    assert agent.choose_defender(table, enemy, []) is None


# ── choose_undefended_target ───────────────────────────────────────────────

def test_choose_undefended_target_returns_hero(agent, table, enemy, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1")
    result = agent.choose_undefended_target(table, enemy)
    assert result in table.player_heroes


def test_choose_undefended_target_invalid_then_valid(agent, table, enemy, monkeypatch):
    responses = iter(["abc", "0", "2"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    result = agent.choose_undefended_target(table, enemy)
    assert result is table.player_heroes[1]


# ── choose_attackers ───────────────────────────────────────────────────────

def test_choose_attackers_blank_returns_empty(agent, table, enemy, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    assert agent.choose_attackers(table, enemy, table.player_heroes) == []


def test_choose_attackers_selects_characters(agent, table, enemy, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1,2")
    result = agent.choose_attackers(table, enemy, table.player_heroes)
    assert result == [table.player_heroes[0], table.player_heroes[1]]


def test_choose_attackers_empty_available_returns_empty(agent, table, enemy):
    assert agent.choose_attackers(table, enemy, []) == []


def test_choose_attackers_result_is_subset_of_available(agent, table, enemy, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "3")
    result = agent.choose_attackers(table, enemy, table.player_heroes)
    assert all(c in table.player_heroes for c in result)
