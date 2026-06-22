import pytest

from agents.expert_agent import ExpertAgent
from src.cards import Ally
from config.limited.cards_registry import CARDS
from config.limited.cards_list import Allies, Enemies, Sphere


@pytest.fixture
def agent():
    return ExpertAgent()


# ── choose_defender ────────────────────────────────────────────────────────

def test_empty_available_returns_none(agent, table):
    enemy = CARDS[Enemies.Dol_Guldur_Orcs].copy()
    assert agent.choose_defender(table, enemy, []) is None


def test_picks_highest_defense_when_no_allies(agent, table):
    # Black_Forest_Bats attack=1 — no hero is doomed; fallback to highest def
    enemy = CARDS[Enemies.Black_Forest_Bats].copy()
    defender = agent.choose_defender(table, enemy, table.player_heroes)
    assert defender.defense == max(h.defense for h in table.player_heroes)


def test_picks_highest_defense_when_ally_survives(agent, table):
    # Beorn (def=3, hp=6) vs Black_Forest_Bats (atk=1): 6 > 1-3 → not doomed
    beorn = CARDS[Allies.Beorn].copy()
    table.player_board.append(beorn)
    enemy = CARDS[Enemies.Black_Forest_Bats].copy()
    available = table.player_heroes + [beorn]
    defender = agent.choose_defender(table, enemy, available)
    # Beorn def=3 beats all heroes def=2 → Beorn chosen
    assert defender is beorn


def test_uses_chump_blocker_over_hero(agent, table):
    # Gondorian_Spearman (def=1, hp=1) vs East_Bight_Patrol (atk=3): 1 <= 3-1=2 → doomed
    spearman = CARDS[Allies.Gondorian_Spearman].copy()
    table.player_board.append(spearman)
    enemy = CARDS[Enemies.East_Bight_Patrol].copy()
    defender = agent.choose_defender(table, enemy, table.player_heroes + [spearman])
    assert defender is spearman


def test_picks_weakest_chump_when_multiple_doomed(agent, table):
    # Gondorian_Spearman (hp=1) and Wandering_Took (hp=2) both doomed vs East_Bight_Patrol (atk=3)
    # Spearman: 1 <= 3-1=2 ✓  Took: 2 <= 3-1=2 ✓ → picks Spearman (min hp)
    spearman = CARDS[Allies.Gondorian_Spearman].copy()
    took     = CARDS[Allies.Wandering_Took].copy()
    table.player_board.extend([spearman, took])
    enemy = CARDS[Enemies.East_Bight_Patrol].copy()
    defender = agent.choose_defender(table, enemy, table.player_heroes + [spearman, took])
    assert defender is spearman


def test_only_heroes_available_picks_highest_defense(agent, table):
    enemy = CARDS[Enemies.Forest_Spider].copy()
    defender = agent.choose_defender(table, enemy, table.player_heroes)
    assert defender.defense == max(h.defense for h in table.player_heroes)


# ── choose_undefended_target ───────────────────────────────────────────────

def test_picks_hero_with_most_hp(agent, table):
    # Thalin max_hp=4, Eowyn/Eleanor max_hp=3
    result = agent.choose_undefended_target(table, None)
    assert result.hit_points == max(h.hit_points for h in table.player_heroes)


def test_single_hero_returned(agent, table):
    table.player_heroes = [table.player_heroes[0]]
    result = agent.choose_undefended_target(table, None)
    assert result is table.player_heroes[0]


def test_picks_most_hp_after_damage(agent, table):
    # Damage the hero that normally has most HP — now another should be chosen
    thalin = max(table.player_heroes, key=lambda h: h.hit_points)
    thalin.take_damage(thalin.hit_points - 1)  # leave 1 HP
    result = agent.choose_undefended_target(table, None)
    assert result is not thalin


# ── choose_attackers ───────────────────────────────────────────────────────

def test_empty_available_returns_empty(agent, table):
    enemy = CARDS[Enemies.Dol_Guldur_Orcs].copy()
    assert agent.choose_attackers(table, enemy, []) == []


def test_minimum_attackers_to_kill(agent, table):
    # Dol_Guldur_Orcs: def=0, hp=3. Thalin(atk=2)+Eleanor(atk=1)=3 → lethal with 2
    enemy = CARDS[Enemies.Dol_Guldur_Orcs].copy()
    attackers = agent.choose_attackers(table, enemy, table.player_heroes)
    total = sum(a.attack for a in attackers) - enemy.defense
    assert total >= enemy.hit_points
    assert len(attackers) < len(table.player_heroes)


def test_one_shot_kill_uses_single_attacker(agent, table):
    # Black_Forest_Bats: def=0, hp=2. Thalin(atk=2) alone is lethal
    enemy = CARDS[Enemies.Black_Forest_Bats].copy()
    attackers = agent.choose_attackers(table, enemy, table.player_heroes)
    assert len(attackers) == 1
    assert attackers[0].attack >= enemy.hit_points


def test_all_attackers_when_cannot_kill(agent, table):
    # Ungoliants_Spawn: def=2, hp=9. All heroes: 1+1+2=4, 4-2=2 < 9 → can't kill
    enemy = CARDS[Enemies.Ungoliants_Spawn].copy()
    attackers = agent.choose_attackers(table, enemy, table.player_heroes)
    assert set(attackers) == set(table.player_heroes)


def test_attackers_with_single_character(agent, table):
    enemy = CARDS[Enemies.Black_Forest_Bats].copy()
    single = [table.player_heroes[0]]
    result = agent.choose_attackers(table, enemy, single)
    assert result == single
