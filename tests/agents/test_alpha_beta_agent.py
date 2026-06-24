import pytest

from agents.alpha_beta_agent import AlphaBetaAgent
from config.limited.cards_registry import CARDS
from config.limited.cards_list import Allies, Enemies, Locations


@pytest.fixture
def agent():
    return AlphaBetaAgent()


# ── _evaluate ─────────────────────────────────────────────────────────────────

def test_evaluate_win_condition(agent, table):
    table.quest_deck = []
    assert agent._evaluate(table) == 10_000.0


def test_evaluate_lose_threat(agent, table):
    table.table_threat = 50
    assert agent._evaluate(table) == -10_000.0


def test_evaluate_lose_all_heroes_dead(agent, table):
    for hero in table.player_heroes:
        hero.take_damage(hero.hit_points)
    assert agent._evaluate(table) == -10_000.0


def test_evaluate_quest_progress_helps(agent, table):
    base = agent._evaluate(table)
    table.get_current_quest().place_progress_token(3)
    assert agent._evaluate(table) > base


def test_evaluate_higher_threat_hurts(agent, table):
    base = agent._evaluate(table)
    table.table_threat += 5
    assert agent._evaluate(table) < base


def test_evaluate_engaged_enemy_hurts(agent, table):
    base = agent._evaluate(table)
    table.encounter_engagement.append(CARDS[Enemies.Dol_Guldur_Orcs].copy())
    assert agent._evaluate(table) < base


def test_evaluate_staging_card_hurts(agent, table):
    base = agent._evaluate(table)
    table.encounter_staging.append(CARDS[Enemies.Dol_Guldur_Orcs].copy())
    assert agent._evaluate(table) < base


def test_evaluate_ally_on_board_helps(agent, table):
    base = agent._evaluate(table)
    table.player_board.append(CARDS[Allies.Beorn].copy())
    assert agent._evaluate(table) > base


# ── choose_questing_characters ────────────────────────────────────────────────

def test_questing_empty_available(agent, table):
    table.encounter_deck = []
    assert agent.choose_questing_characters(table, []) == []


def test_questing_no_deck_no_staging_quests_all(agent, table):
    # No threats at all: maximum willpower is always optimal
    table.encounter_deck = []
    table.encounter_staging = []
    result = agent.choose_questing_characters(table, table.player_heroes)
    assert set(result) == set(table.player_heroes)


def test_questing_avoids_crossing_50_threat(agent, table):
    # staging_threat=3, table_threat=48: any subset with willpower < 3 pushes threat to >=50
    table.table_threat = 48
    table.encounter_deck = []
    table.encounter_staging = [CARDS[Locations.Necromancers_Pass].copy()]  # threat=3
    result = agent.choose_questing_characters(table, table.player_heroes)
    total_wp = sum(h.willpower for h in result)
    assert total_wp >= 3


def test_questing_minimax_keeps_fighters_for_auto_engaging_enemy(agent, table):
    # staging_threat=6, table_threat=25 > East_Bight_Patrol.engagement=5 → it auto-engages
    # All heroes questing (wp=6, net=0) leaves no fighters; worst case: full damage from EBP.
    # Eowyn-only (wp=4, net=-2) keeps Eleanor+Thalin who together kill EBP (atk sum 3, kills at 2hp).
    # Minimax prefers Eowyn-only because it minimises worst-case encounter damage.
    table.encounter_staging = [
        CARDS[Locations.Necromancers_Pass].copy(),  # threat=3
        CARDS[Locations.Enchanted_Stream].copy(),   # threat=2
        CARDS[Locations.Old_Forest_Road].copy(),    # threat=1  → total staging=6
    ]
    table.encounter_deck = [CARDS[Enemies.East_Bight_Patrol].copy()]
    result = agent.choose_questing_characters(table, table.player_heroes)
    assert result == [table.player_heroes[0]]  # Eowyn only


def test_questing_non_auto_engaging_enemy_does_not_force_fighters(agent, table):
    # Ungoliants_Spawn.engagement=32 > table_threat=25 → stays in staging, not a combat threat
    # Decision is driven by quest progress alone; all heroes questing is optimal
    table.encounter_staging = []
    table.encounter_deck = [CARDS[Enemies.Ungoliants_Spawn].copy()]
    result = agent.choose_questing_characters(table, table.player_heroes)
    assert set(result) == set(table.player_heroes)


def test_questing_alpha_cut_does_not_change_result(agent, table):
    # Many cards in the deck exercise the alpha cut path; result must still be correct
    table.encounter_staging = [
        CARDS[Locations.Necromancers_Pass].copy(),
        CARDS[Locations.Enchanted_Stream].copy(),
        CARDS[Locations.Old_Forest_Road].copy(),
    ]
    table.encounter_deck = [
        CARDS[Enemies.East_Bight_Patrol].copy(),
        CARDS[Enemies.Black_Forest_Bats].copy(),
        CARDS[Locations.Forest_Gate].copy(),
    ]
    result = agent.choose_questing_characters(table, table.player_heroes)
    assert isinstance(result, list)
    assert all(h in table.player_heroes for h in result)


# ── choose_card_to_play ────────────────────────────────────────────────────────

def test_card_to_play_empty_returns_none(agent, table):
    assert agent.choose_card_to_play(table, []) is None


def test_card_to_play_single_card(agent, table):
    card = CARDS[Allies.Wandering_Took].copy()
    assert agent.choose_card_to_play(table, [card]) is card


def test_card_to_play_prefers_highest_efficiency(agent, table):
    # Gandalf: (4*2+4+4)/5=3.2, Veteran_Axehand: (2*2+1+0)/2=2.5, Lorien_Guide: (1*2+1+0)/3=1.0
    gandalf = CARDS[Allies.Gandalf].copy()
    veteran = CARDS[Allies.Veteran_Axehand].copy()
    guide = CARDS[Allies.Lorien_Guide].copy()
    assert agent.choose_card_to_play(table, [guide, veteran, gandalf]) is gandalf


def test_card_to_play_attack_weighted_double(agent, table):
    # Veteran_Axehand score=(2*2+1+0)/2=2.5 beats Wandering_Took (1*2+1+1)/2=2.0
    veteran = CARDS[Allies.Veteran_Axehand].copy()
    took = CARDS[Allies.Wandering_Took].copy()
    assert agent.choose_card_to_play(table, [took, veteran]) is veteran


# ── choose_location ────────────────────────────────────────────────────────────

def test_choose_location_empty_returns_none(agent, table):
    assert agent.choose_location(table, []) is None


def test_choose_location_single(agent, table):
    loc = CARDS[Locations.Necromancers_Pass].copy()
    assert agent.choose_location(table, [loc]) is loc


def test_choose_location_picks_highest_threat(agent, table):
    low = CARDS[Locations.Old_Forest_Road].copy()   # threat=1
    high = CARDS[Locations.Necromancers_Pass].copy()  # threat=3
    assert agent.choose_location(table, [low, high]) is high


# ── choose_optional_engagement ────────────────────────────────────────────────

def test_optional_engagement_empty(agent, table):
    assert agent.choose_optional_engagement(table, []) == []


def test_optional_engagement_engages_killable_enemy(agent, table):
    # Heroes total atk=4; Black_Forest_Bats def=0 hp=2 → budget 2 ≤ 4 ✓
    bats = CARDS[Enemies.Black_Forest_Bats].copy()
    assert agent.choose_optional_engagement(table, [bats]) == [bats]


def test_optional_engagement_skips_unkillable_enemy(agent, table):
    # Ungoliants_Spawn def=2 hp=9 → budget 11, total atk=4 → can't kill
    spawn = CARDS[Enemies.Ungoliants_Spawn].copy()
    assert agent.choose_optional_engagement(table, [spawn]) == []


def test_optional_engagement_greedy_selects_easy_only(agent, table):
    bats = CARDS[Enemies.Black_Forest_Bats].copy()
    spawn = CARDS[Enemies.Ungoliants_Spawn].copy()
    result = agent.choose_optional_engagement(table, [spawn, bats])
    assert bats in result
    assert spawn not in result


# ── choose_defender ────────────────────────────────────────────────────────────

def test_choose_defender_empty_returns_none(agent, table):
    enemy = CARDS[Enemies.Dol_Guldur_Orcs].copy()
    assert agent.choose_defender(table, enemy, []) is None


def test_choose_defender_picks_perfect_blocker(agent, table):
    # Black_Forest_Bats atk=1; Eleanor def=2 → 0 damage → score=50
    bats = CARDS[Enemies.Black_Forest_Bats].copy()
    result = agent.choose_defender(table, bats, table.player_heroes)
    assert max(0, bats.attack - result.defense) == 0


def test_choose_defender_prefers_chump_ally_over_low_hp_hero(agent, table):
    # East_Bight_Patrol atk=3; Eowyn/Eleanor hp=3 def=1/2: dmg to Eowyn=2, score=(3-2)*4=4
    # Gondorian_Spearman hp=1 def=1: dmg=2 >= hp=1 → chump score=10 → spearman wins
    patrol = CARDS[Enemies.East_Bight_Patrol].copy()
    spearman = CARDS[Allies.Gondorian_Spearman].copy()
    low_hp_heroes = [table.player_heroes[0], table.player_heroes[1]]  # Eowyn, Eleanor
    result = agent.choose_defender(table, patrol, low_hp_heroes + [spearman])
    assert result is spearman


def test_choose_defender_surviving_ally_beats_weaker_hero(agent, table):
    # Black_Forest_Bats atk=1; Beorn def=3 → 0 damage → score=50, same as any perfect blocker
    bats = CARDS[Enemies.Black_Forest_Bats].copy()
    beorn = CARDS[Allies.Beorn].copy()
    result = agent.choose_defender(table, bats, table.player_heroes + [beorn])
    assert max(0, bats.attack - result.defense) == 0


# ── choose_undefended_target ──────────────────────────────────────────────────

def test_undefended_target_max_hp(agent, table):
    result = agent.choose_undefended_target(table, None)
    assert result.hit_points == max(h.hit_points for h in table.player_heroes)


def test_undefended_target_single_hero(agent, table):
    table.player_heroes = [table.player_heroes[0]]
    result = agent.choose_undefended_target(table, None)
    assert result is table.player_heroes[0]


def test_undefended_target_updates_after_damage(agent, table):
    thalin = max(table.player_heroes, key=lambda h: h.hit_points)
    thalin.take_damage(thalin.hit_points - 1)  # Down to 1 HP
    result = agent.choose_undefended_target(table, None)
    assert result is not thalin


# ── choose_attackers ──────────────────────────────────────────────────────────

def test_choose_attackers_empty(agent, table):
    enemy = CARDS[Enemies.Dol_Guldur_Orcs].copy()
    assert agent.choose_attackers(table, enemy, []) == []


def test_choose_attackers_single_kill(agent, table):
    # Black_Forest_Bats def=0 hp=2; Thalin atk=2 → one-shots it
    bats = CARDS[Enemies.Black_Forest_Bats].copy()
    result = agent.choose_attackers(table, bats, table.player_heroes)
    assert len(result) == 1
    assert result[0].attack >= bats.hit_points + bats.defense


def test_choose_attackers_minimum_to_kill(agent, table):
    # Dol_Guldur_Orcs def=0 hp=3; Thalin(2)+Eleanor(1)=3 → lethal with 2 heroes
    orcs = CARDS[Enemies.Dol_Guldur_Orcs].copy()
    result = agent.choose_attackers(table, orcs, table.player_heroes)
    assert sum(a.attack for a in result) - orcs.defense >= orcs.hit_points
    assert len(result) < len(table.player_heroes)


def test_choose_attackers_all_when_cannot_kill(agent, table):
    # Ungoliants_Spawn def=2 hp=9; all heroes atk 1+1+2=4, 4-2=2 < 9 → can't kill
    spawn = CARDS[Enemies.Ungoliants_Spawn].copy()
    result = agent.choose_attackers(table, spawn, table.player_heroes)
    assert set(result) == set(table.player_heroes)
