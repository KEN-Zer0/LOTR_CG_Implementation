import pytest
from src.game.phases.refresh_phase import RefreshPhase
from src.cards import Ally
from config.limited.cards_list import Allies, Sphere


def test_readies_all_exhausted_heroes(table):
    """All heroes are ready (not exhausted) after execute."""
    phase = RefreshPhase(table)
    for hero in table.player_heroes:
        hero.exhaust()
    phase.execute()
    for hero in table.player_heroes:
        assert not hero.exhausted


def test_readies_board_allies(table):
    """Allies on the player board are readied during execute."""
    phase = RefreshPhase(table)
    ally = Ally(Allies.Gandalf, 4, 4, 4, 4, Sphere.Neutral, 5)
    ally.exhaust()
    table.player_board.append(ally)
    phase.execute()
    assert not ally.exhausted


def test_raises_threat_by_exactly_one(table):
    """table_threat increases by exactly 1 after execute."""
    phase = RefreshPhase(table)
    before = table.table_threat
    phase.execute()
    assert table.table_threat == before + 1


def test_ready_character_clears_exhausted_flag(table):
    """ready_character removes the exhausted flag from a single character."""
    phase = RefreshPhase(table)
    hero = table.player_heroes[0]
    hero.exhaust()
    phase.ready_character(hero)
    assert not hero.exhausted


def test_raise_threat_level(table):
    """raise_threat_level increments table_threat by 1."""
    phase = RefreshPhase(table)
    before = table.table_threat
    phase.raise_threat_level()
    assert table.table_threat == before + 1
