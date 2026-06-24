import pytest
from src.game.game import Game
from config.limited.cards_list import Enemies


@pytest.fixture
def game():
    return Game()


def test_setup_deals_opening_hand(game):
    """Player hand contains 6 cards after game initialization."""
    assert len(game.table.player_hand) == 6


def test_setup_places_ungoliants_spawn_in_staging(game):
    """Ungoliants_Spawn is in the encounter staging area after setup."""
    assert any(c.name == Enemies.Ungoliants_Spawn for c in game.table.encounter_staging)


def test_setup_removes_ungoliants_spawn_from_encounter_deck(game):
    """Ungoliants_Spawn is not left in the encounter deck after setup."""
    assert not any(c.name == Enemies.Ungoliants_Spawn for c in game.table.encounter_deck)
