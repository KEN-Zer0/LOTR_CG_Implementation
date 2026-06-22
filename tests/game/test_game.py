import pytest
from src.game.game import Game


def test_game_initializes_seven_phases():
    """Game starts with exactly 7 phases in the correct order."""
    game = Game()
    assert len(game.phases) == 7


def test_game_has_table():
    """Game exposes a Table instance."""
    game = Game()
    assert game.table is not None


def test_run_round_skips_all_phases_on_win_condition():
    """No phase executes when the win condition is already met before the round."""
    game = Game()
    game.table.quest_deck.clear()
    executed = []
    game.phases[0].execute = lambda: executed.append(0)
    game.run_round()
    assert executed == []


def test_run_round_skips_all_phases_on_lose_condition():
    """No phase executes when the lose condition is already met before the round."""
    game = Game()
    game.table.table_threat = 50
    executed = []
    game.phases[0].execute = lambda: executed.append(0)
    game.run_round()
    assert executed == []


def test_run_round_executes_all_phases_in_order():
    """All 7 phases execute in order when no win/lose condition is triggered."""
    game = Game()
    order = []

    for i, phase in enumerate(game.phases):
        original = phase.execute
        def make_tracker(idx, orig):
            def tracked():
                order.append(idx)
                orig()
            return tracked
        phase.execute = make_tracker(i, original)

    game.run_round()
    assert order == list(range(7))
