import pytest
from src.game.phases.planning_phase import PlanningPhase
from src.cards import Ally
from config.limited.cards_list import Allies, Sphere
from config.limited.cards_registry import CARDS


@pytest.fixture
def cheap_ally():
    return Ally(Allies.Gondorian_Spearman, 1, 1, 1, 0, Sphere.Tactics, 1)


@pytest.fixture
def expensive_ally():
    return Ally(Allies.Beorn, 3, 3, 6, 1, Sphere.Tactics, 6)


def test_plays_affordable_card(table, cheap_ally):
    """Affordable card moves from hand to board after execute."""
    phase = PlanningPhase(table)
    table.player_heroes[0].change_resource_pool(5)
    table.player_hand.append(cheap_ally)
    phase.execute()
    assert cheap_ally in table.player_board
    assert cheap_ally not in table.player_hand


def test_does_not_play_unaffordable_card(table, expensive_ally):
    """Card whose cost exceeds available resources stays in hand."""
    phase = PlanningPhase(table)
    table.player_hand.append(expensive_ally)
    phase.execute()
    assert expensive_ally not in table.player_board
    assert expensive_ally in table.player_hand


def test_deducts_resources_after_playing(table, cheap_ally):
    """Total resources decrease by the played card's cost."""
    phase = PlanningPhase(table)
    table.player_heroes[0].change_resource_pool(3)
    table.player_hand.append(cheap_ally)
    before = sum(h.resource_pool for h in table.player_heroes)
    phase.execute()
    after = sum(h.resource_pool for h in table.player_heroes)
    assert after == before - cheap_ally.cost


def test_choose_card_returns_cheapest(table):
    """_choose_card selects the card with the lowest cost."""
    phase = PlanningPhase(table)
    a = Ally(Allies.Gondorian_Spearman, 1, 1, 1, 0, Sphere.Tactics, 1)
    b = Ally(Allies.Beorn, 3, 3, 6, 1, Sphere.Tactics, 6)
    assert phase._choose_card([b, a]) is a


def test_plays_cheapest_when_resources_limited(table):
    """Cheapest card is played when resources cover only one card."""
    phase = PlanningPhase(table)
    cheap = Ally(Allies.Gondorian_Spearman, 1, 1, 1, 0, Sphere.Tactics, 1)
    pricey = Ally(Allies.Beorn, 3, 3, 6, 1, Sphere.Tactics, 6)
    table.player_heroes[0].change_resource_pool(1)
    table.player_hand.extend([pricey, cheap])
    phase.execute()
    assert cheap in table.player_board
    assert pricey in table.player_hand


def test_total_resources_sums_all_heroes(table):
    """_total_resources returns the combined resource pool of all heroes."""
    phase = PlanningPhase(table)
    table.player_heroes[0].change_resource_pool(3)
    table.player_heroes[1].change_resource_pool(2)
    assert phase._total_resources() == 5


def test_pay_for_card_spends_from_richest_hero(table):
    """Resources are deducted from the hero with the most tokens first."""
    phase = PlanningPhase(table)
    table.player_heroes[0].change_resource_pool(5)
    table.player_heroes[1].change_resource_pool(1)
    card = Ally(Allies.Gandalf, 4, 4, 4, 4, Sphere.Neutral, 4)
    phase._pay_for_card(card)
    assert table.player_heroes[0].resource_pool == 1
    assert table.player_heroes[1].resource_pool == 1


def test_multiple_cards_played_in_one_phase(table):
    """All affordable cards are played before the phase ends."""
    phase = PlanningPhase(table)
    table.player_heroes[0].change_resource_pool(4)
    a = Ally(Allies.Gondorian_Spearman, 1, 1, 1, 0, Sphere.Tactics, 1)
    b = Ally(Allies.Wandering_Took, 1, 1, 2, 1, Sphere.Spirit, 2)
    table.player_hand.extend([a, b])
    phase.execute()
    assert a in table.player_board
    assert b in table.player_board
