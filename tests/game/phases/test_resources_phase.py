import pytest
from src.game.phases.resources_phase import ResourcesPhase


def test_execute_adds_one_resource_to_each_hero(table):
    """Each hero gains exactly 1 resource after execute."""
    phase = ResourcesPhase(table)
    before = [h.resource_pool for h in table.player_heroes]
    phase.execute()
    for i, hero in enumerate(table.player_heroes):
        assert hero.resource_pool == before[i] + 1


def test_execute_draws_one_card(table):
    """One card moves from player deck to hand after execute."""
    phase = ResourcesPhase(table)
    before_hand = len(table.player_hand)
    before_deck = len(table.player_deck)
    phase.execute()
    assert len(table.player_hand) == before_hand + 1
    assert len(table.player_deck) == before_deck - 1


def test_execute_empty_deck_no_crash(table):
    """No card drawn and no error when player deck is empty."""
    phase = ResourcesPhase(table)
    table.player_deck.clear()
    hand_before = len(table.player_hand)
    phase.execute()
    assert len(table.player_hand) == hand_before


def test_increase_hero_resource(table):
    """increase_hero_resource adds exactly 1 resource to the given hero."""
    phase = ResourcesPhase(table)
    hero = table.player_heroes[0]
    phase.increase_hero_resource(hero)
    assert hero.resource_pool == 1


def test_increase_heroes_resource(table):
    """increase_heroes_resource adds 1 resource to every hero."""
    phase = ResourcesPhase(table)
    phase.increase_heroes_resource()
    for hero in table.player_heroes:
        assert hero.resource_pool == 1


def test_draw_one_card_from_player_deck(table):
    """draw_one_card_from_player_deck moves the top card to hand."""
    phase = ResourcesPhase(table)
    before = len(table.player_hand)
    phase.draw_one_card_from_player_deck()
    assert len(table.player_hand) == before + 1
