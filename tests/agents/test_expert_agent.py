import pytest

from agents.expert_agent import ExpertAgent
from src.cards import Ally, Enemy, Location
from config.limited.cards_list import Allies, Enemies, Locations, Sphere


@pytest.fixture
def agent():
    return ExpertAgent()


# ── choose_questing_characters ─────────────────────────────────────────────

def test_questing_commits_all_available(agent, table):
    result = agent.choose_questing_characters(table, table.player_heroes)
    assert result == table.player_heroes


def test_questing_empty_input_returns_empty(agent, table):
    assert agent.choose_questing_characters(table, []) == []


# ── choose_card_to_play ────────────────────────────────────────────────────

def test_choose_card_picks_cheapest(agent, table):
    cheap = Ally(Allies.Gondorian_Spearman, 1, 0, 2, 0, Sphere.Tactics, 2)
    expensive = Ally(Allies.Lorien_Guide, 0, 0, 2, 2, Sphere.Spirit, 4)
    assert agent.choose_card_to_play(table, [expensive, cheap]) is cheap


def test_choose_card_single_card_returned(agent, table):
    card = Ally(Allies.Wandering_Took, 0, 0, 2, 1, Sphere.Spirit, 1)
    assert agent.choose_card_to_play(table, [card]) is card


# ── choose_location ────────────────────────────────────────────────────────

def test_choose_location_picks_highest_threat(agent, table):
    low = Location(Locations.Old_Forest_Road, 1, 3)
    high = Location(Locations.Mountains_of_Mirkwood, 3, 4)
    assert agent.choose_location(table, [low, high]) is high


def test_choose_location_single_location_returned(agent, table):
    loc = Location(Locations.Forest_Gate, 2, 3)
    assert agent.choose_location(table, [loc]) is loc


# ── choose_optional_engagement ─────────────────────────────────────────────

def test_optional_engagement_always_empty(agent, table):
    enemies = [Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2)]
    assert agent.choose_optional_engagement(table, enemies) == []


# ── choose_defender ────────────────────────────────────────────────────────

def test_choose_defender_empty_available_returns_none(agent, table):
    enemy = Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2)
    assert agent.choose_defender(table, enemy, []) is None


def test_choose_defender_picks_highest_defense_when_no_chump(agent, table):
    # attack=1 — no hero has hp <= 1-defense, so no chump; fallback to highest def
    enemy = Enemy(Enemies.Dol_Guldur_Orcs, 1, 0, 3, 10, 1)
    defender = agent.choose_defender(table, enemy, table.player_heroes)
    assert defender.defense == max(h.defense for h in table.player_heroes)


def test_choose_defender_uses_chump_blocker_over_hero(agent, table):
    # enemy.attack=5; ally: def=0, hp=1 → doomed (1 <= 5-0=5)
    doomed = Ally(Allies.Gondorian_Spearman, 1, 0, 1, 0, Sphere.Tactics, 2)
    table.player_board.append(doomed)
    enemy = Enemy(Enemies.Ungoliants_Spawn, 5, 2, 9, 32, 3)
    defender = agent.choose_defender(table, enemy, table.player_heroes + [doomed])
    assert defender is doomed


def test_choose_defender_ignores_ally_that_survives(agent, table):
    # enemy.attack=1; ally: def=0, hp=5 → not doomed (5 > 1-0=1) → falls back to highest def
    tough = Ally(Allies.Gondorian_Spearman, 1, 0, 5, 0, Sphere.Tactics, 2)
    table.player_board.append(tough)
    enemy = Enemy(Enemies.Dol_Guldur_Orcs, 1, 0, 3, 10, 1)
    available = table.player_heroes + [tough]
    defender = agent.choose_defender(table, enemy, available)
    assert defender.defense == max(c.defense for c in available)


def test_choose_defender_picks_weakest_chump_when_multiple_doomed(agent, table):
    # Two doomed allies — agent should pick the one with fewer HP
    weak = Ally(Allies.Gondorian_Spearman, 1, 0, 1, 0, Sphere.Tactics, 2)
    medium = Ally(Allies.Veteran_Axehand, 2, 0, 2, 0, Sphere.Tactics, 2)
    table.player_board.extend([weak, medium])
    enemy = Enemy(Enemies.Ungoliants_Spawn, 5, 0, 9, 32, 3)
    defender = agent.choose_defender(table, enemy, table.player_heroes + [weak, medium])
    assert defender is weak


# ── choose_undefended_target ───────────────────────────────────────────────

def test_choose_undefended_target_picks_hero_with_most_hp(agent, table):
    # Thalin has 4 HP; Eowyn and Eleanor have 3 HP
    result = agent.choose_undefended_target(table, None)
    assert result.hit_points == max(h.hit_points for h in table.player_heroes)


def test_choose_undefended_target_single_hero(agent, table):
    table.player_heroes = [table.player_heroes[0]]
    result = agent.choose_undefended_target(table, None)
    assert result is table.player_heroes[0]


# ── choose_attackers ───────────────────────────────────────────────────────

def test_choose_attackers_empty_available_returns_empty(agent, table):
    enemy = Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2)
    assert agent.choose_attackers(table, enemy, []) == []


def test_choose_attackers_minimum_subset_to_kill(agent, table):
    # Heroes: Thalin(atk=2), Eowyn(atk=1), Eleanor(atk=1)
    # Enemy: def=0, hp=3. Thalin alone: 2 < 3. Thalin+any(1): 3 >= 3 → 2 attackers, not 3.
    enemy = Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2)
    attackers = agent.choose_attackers(table, enemy, table.player_heroes)
    total_damage = sum(a.attack for a in attackers) - enemy.defense
    assert total_damage >= enemy.hit_points
    assert len(attackers) < len(table.player_heroes)


def test_choose_attackers_all_characters_when_cannot_kill(agent, table):
    # Enemy too tough to kill with available heroes
    tank = Enemy(Enemies.Ungoliants_Spawn, 5, 2, 100, 32, 3)
    attackers = agent.choose_attackers(table, tank, table.player_heroes)
    assert set(attackers) == set(table.player_heroes)


def test_choose_attackers_one_shot_kill_uses_single_attacker(agent, table):
    # Enemy with 1 HP, def=0 — Thalin(atk=2) alone is lethal
    easy = Enemy(Enemies.Black_Forest_Bats, 1, 0, 1, 5, 1)
    attackers = agent.choose_attackers(table, easy, table.player_heroes)
    assert len(attackers) == 1
    assert attackers[0].attack >= easy.hit_points
