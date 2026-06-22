import pytest
from src.table.table import Table
from src.cards import Hero, Enemy, Location
from config.limited.cards_list import Heroes, Enemies, Locations, Sphere
from config.constants import GameConstants


def test_initial_threat_equals_sum_of_hero_threats(table):
    """Starting table_threat equals the sum of all hero threat values (9+7+9=25)."""
    assert table.table_threat == 25


def test_draw_player_card_moves_to_hand(table):
    """draw_player_card removes the top card from the deck and adds it to hand."""
    before_deck = len(table.player_deck)
    card = table.draw_player_card()
    assert card is not None
    assert card in table.player_hand
    assert len(table.player_deck) == before_deck - 1


def test_draw_player_card_returns_none_when_empty(table):
    """draw_player_card returns None and leaves hand unchanged when deck is empty."""
    table.player_deck.clear()
    result = table.draw_player_card()
    assert result is None
    assert table.player_hand == []


def test_reveal_encounter_card_moves_to_staging(table):
    """reveal_encounter_card pops the top card into the staging area."""
    before = len(table.encounter_deck)
    card = table.reveal_encounter_card()
    assert card is not None
    assert card in table.encounter_staging
    assert len(table.encounter_deck) == before - 1


def test_reveal_encounter_card_reshuffles_discard_when_deck_empty(table):
    """When the encounter deck is empty, the discard pile is reshuffled into it."""
    table.encounter_deck.clear()
    enemy = Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2)
    table.encounter_discard.append(enemy)
    card = table.reveal_encounter_card()
    assert card is not None
    assert card in table.encounter_staging
    assert table.encounter_discard == []


def test_reveal_encounter_card_returns_none_when_both_empty(table):
    """Returns None when both encounter deck and discard are empty."""
    table.encounter_deck.clear()
    table.encounter_discard.clear()
    assert table.reveal_encounter_card() is None


def test_get_current_quest_returns_first_quest(table):
    """get_current_quest returns the first element of the quest deck."""
    assert table.get_current_quest() is table.quest_deck[0]


def test_check_win_condition_false_initially(table):
    """Win condition is not met at game start."""
    assert table.check_win_condition() is False


def test_check_win_condition_true_when_quest_deck_empty(table):
    """Win condition is met when the quest deck is empty."""
    table.quest_deck.clear()
    assert table.check_win_condition() is True


def test_check_lose_condition_false_initially(table):
    """Lose condition is not met at game start."""
    assert table.check_lose_condition() is False


def test_check_lose_condition_true_at_threat_50(table):
    """Lose condition is met when table_threat reaches LOSING_THREAT."""
    table.table_threat = GameConstants.LOSING_THREAT
    assert table.check_lose_condition() is True


def test_check_lose_condition_true_when_all_heroes_dead(table):
    """Lose condition is met when all heroes have 0 HP."""
    for hero in table.player_heroes:
        hero._hit_points = 0
    assert table.check_lose_condition() is True


def test_is_threat_too_high_at_exactly_50(table):
    """is_threat_too_high returns True at exactly the LOSING_THREAT threshold."""
    table.table_threat = 50
    assert table.is_threat_too_high() is True


def test_is_threat_too_high_false_below_50(table):
    """is_threat_too_high returns False when threat is below the threshold."""
    table.table_threat = 49
    assert table.is_threat_too_high() is False


def test_are_all_heroes_dead_false_when_any_alive(table):
    """are_all_heroes_dead returns False when at least one hero is alive."""
    table.player_heroes[0]._hit_points = 0
    assert table.are_all_heroes_dead() is False


def test_are_all_heroes_dead_true_when_all_at_zero(table):
    """are_all_heroes_dead returns True when all heroes have 0 HP."""
    for hero in table.player_heroes:
        hero._hit_points = 0
    assert table.are_all_heroes_dead() is True


def test_calculate_table_threat(table):
    """calculate_table_threat recomputes threat from the current hero list."""
    table.table_threat = 0
    table.calculate_table_threat()
    assert table.table_threat == 25
