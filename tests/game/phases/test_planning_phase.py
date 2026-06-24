import pytest
from src.game.phases.planning_phase import PlanningPhase
from config.limited.cards_list import Allies, Sphere
from config.limited.cards_registry import CARDS


@pytest.fixture
def cheap_ally():
    return CARDS[Allies.Wandering_Took].copy()  # Spirit, cost=2


@pytest.fixture
def expensive_ally():
    return CARDS[Allies.Beorn].copy()  # Tactics, cost=6


def test_plays_affordable_card(table, cheap_ally):
    """Affordable Spirit card moves from hand to board after execute."""
    phase = PlanningPhase(table)
    table.player_heroes[0].change_resource_pool(5)  # Eowyn (Spirit)
    table.player_hand.append(cheap_ally)
    phase.execute()
    assert cheap_ally in table.player_board
    assert cheap_ally not in table.player_hand


def test_does_not_play_unaffordable_card(table, expensive_ally):
    """Card whose cost exceeds available sphere resources stays in hand."""
    phase = PlanningPhase(table)
    table.player_hand.append(expensive_ally)
    phase.execute()
    assert expensive_ally not in table.player_board
    assert expensive_ally in table.player_hand


def test_deducts_resources_after_playing(table, cheap_ally):
    """Total resources in matching sphere decrease by the played card's cost."""
    phase = PlanningPhase(table)
    table.player_heroes[0].change_resource_pool(3)  # Eowyn (Spirit)
    table.player_hand.append(cheap_ally)
    before = sum(h.resource_pool for h in table.player_heroes)
    phase.execute()
    after = sum(h.resource_pool for h in table.player_heroes)
    assert after == before - cheap_ally.cost


def test_choose_card_returns_cheapest(table):
    """_choose_card selects the card with the lowest cost."""
    phase = PlanningPhase(table)
    a = CARDS[Allies.Gondorian_Spearman].copy()  # cost=2
    b = CARDS[Allies.Beorn].copy()               # cost=6
    assert phase._choose_card([b, a]) is a


def test_plays_cheapest_when_resources_limited(table):
    """Cheapest card is played when resources cover only one card within its sphere."""
    phase = PlanningPhase(table)
    cheap = CARDS[Allies.Gondorian_Spearman].copy()  # Tactics, cost=2
    pricey = CARDS[Allies.Beorn].copy()              # Tactics, cost=6
    table.player_heroes[2].change_resource_pool(2)   # Thalin (Tactics)
    table.player_hand.extend([pricey, cheap])
    phase.execute()
    assert cheap in table.player_board
    assert pricey in table.player_hand


def test_resources_for_sphere_sums_matching_heroes(table):
    """_resources_for_sphere returns only the resources of heroes in that sphere."""
    phase = PlanningPhase(table)
    table.player_heroes[0].change_resource_pool(3)  # Eowyn (Spirit)
    table.player_heroes[1].change_resource_pool(2)  # Eleanor (Spirit)
    table.player_heroes[2].change_resource_pool(4)  # Thalin (Tactics) — must not be counted
    assert phase._resources_for_sphere(Sphere.Spirit) == 5
    assert phase._resources_for_sphere(Sphere.Tactics) == 4


def test_pay_for_card_spends_from_richest_hero(table):
    """Resources are deducted from the hero with the most tokens first."""
    phase = PlanningPhase(table)
    table.player_heroes[0].change_resource_pool(6)  # Eowyn (Spirit)
    table.player_heroes[1].change_resource_pool(1)  # Eleanor (Spirit)
    card = CARDS[Allies.Gandalf].copy()             # Neutral, cost=5 — any hero can pay
    phase._pay_for_card(card)
    assert table.player_heroes[0].resource_pool == 1  # 6 - 5 = 1
    assert table.player_heroes[1].resource_pool == 1


def test_multiple_cards_played_in_one_phase(table):
    """Cards of different spheres are both played when matching heroes have enough resources."""
    phase = PlanningPhase(table)
    table.player_heroes[0].change_resource_pool(2)  # Eowyn (Spirit)
    table.player_heroes[2].change_resource_pool(2)  # Thalin (Tactics)
    a = CARDS[Allies.Gondorian_Spearman].copy()     # Tactics, cost=2
    b = CARDS[Allies.Wandering_Took].copy()          # Spirit, cost=2
    table.player_hand.extend([a, b])
    phase.execute()
    assert a in table.player_board
    assert b in table.player_board
