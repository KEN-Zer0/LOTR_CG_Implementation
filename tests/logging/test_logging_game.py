import pytest

from config.limited.cards_list import Heroes, Allies, Enemies, Locations, Sphere
from config.log_constants import SnapshotKey, StatKey, PhaseKey
from src.logging.logger import Logger
from src.game.logging_game import LoggingGame
from src.game.log_formatters import _HeroSnap, _AllySnap


@pytest.fixture(autouse=True)
def reset_logger():
    yield
    Logger.close()


@pytest.fixture
def game():
    return LoggingGame()


def _h(name=Heroes.Eowyn, hp=5, max_hp=5, res=0, exhausted=False, sphere=Sphere.Spirit, willpower=1) -> _HeroSnap:
    return _HeroSnap(name, hp, max_hp, res, exhausted, sphere, willpower)


def _a(name=Allies.Gondorian_Spearman, hp=2, max_hp=2, exhausted=False, willpower=1) -> _AllySnap:
    return _AllySnap(name, hp, max_hp, exhausted, willpower)


def _snap(**overrides) -> dict:
    base = {
        SnapshotKey.THREAT:              0,
        SnapshotKey.HEROES:              [],
        SnapshotKey.BOARD:               [],
        SnapshotKey.STAGING:             [],
        SnapshotKey.ENGAGED:             [],
        SnapshotKey.HAND:                [],
        SnapshotKey.QUEST_NAME:          None,
        SnapshotKey.QUEST_PROGRESS:      None,
        SnapshotKey.QUEST_REQUIRED:      None,
        SnapshotKey.ACTIVE_LOC:          None,
        SnapshotKey.ACTIVE_LOC_PROGRESS: None,
        SnapshotKey.TOTAL_RESOURCES:     0,
    }
    base.update(overrides)
    return base


class TestLoggingGameInit:
    def test_round_starts_at_zero(self, game):
        assert game._round == 0

    def test_all_stats_start_at_zero(self, game):
        for key in StatKey:
            assert game._stats[key] == 0


class TestUpdateStatsResources:
    def test_resources_generated_on_increase(self, game):
        game._update_stats(_snap(total_resources=3), _snap(total_resources=6), PhaseKey.RESOURCES)
        assert game._stats[StatKey.RESOURCES_GENERATED] == 3

    def test_resources_generated_accumulates(self, game):
        game._update_stats(_snap(total_resources=0), _snap(total_resources=3), PhaseKey.RESOURCES)
        game._update_stats(_snap(total_resources=0), _snap(total_resources=3), PhaseKey.RESOURCES)
        assert game._stats[StatKey.RESOURCES_GENERATED] == 6

    def test_resources_generated_ignores_decrease(self, game):
        game._update_stats(_snap(total_resources=6), _snap(total_resources=3), PhaseKey.RESOURCES)
        assert game._stats[StatKey.RESOURCES_GENERATED] == 0

    def test_resources_generated_only_in_resources_phase(self, game):
        game._update_stats(_snap(total_resources=0), _snap(total_resources=3), PhaseKey.PLANNING)
        assert game._stats[StatKey.RESOURCES_GENERATED] == 0

    def test_resources_spent_on_decrease(self, game):
        game._update_stats(_snap(total_resources=6), _snap(total_resources=4), PhaseKey.PLANNING)
        assert game._stats[StatKey.RESOURCES_SPENT] == 2

    def test_resources_spent_accumulates(self, game):
        game._update_stats(_snap(total_resources=6), _snap(total_resources=4), PhaseKey.PLANNING)
        game._update_stats(_snap(total_resources=4), _snap(total_resources=2), PhaseKey.PLANNING)
        assert game._stats[StatKey.RESOURCES_SPENT] == 4

    def test_resources_spent_ignores_increase(self, game):
        game._update_stats(_snap(total_resources=3), _snap(total_resources=6), PhaseKey.PLANNING)
        assert game._stats[StatKey.RESOURCES_SPENT] == 0

    def test_resources_spent_only_in_planning_phase(self, game):
        game._update_stats(_snap(total_resources=6), _snap(total_resources=4), PhaseKey.COMBAT)
        assert game._stats[StatKey.RESOURCES_SPENT] == 0


class TestUpdateStatsAllies:
    def test_ally_entering_board_counted(self, game):
        before = _snap(board=[_a(Allies.Gondorian_Spearman)])
        after  = _snap(board=[_a(Allies.Gondorian_Spearman), _a(Allies.Wandering_Took)])
        game._update_stats(before, after, PhaseKey.PLANNING)
        assert game._stats[StatKey.ALLIES_PLAYED] == 1

    def test_ally_leaving_board_not_counted(self, game):
        before = _snap(board=[_a(Allies.Gondorian_Spearman), _a(Allies.Wandering_Took)])
        after  = _snap(board=[_a(Allies.Gondorian_Spearman)])
        game._update_stats(before, after, PhaseKey.PLANNING)
        assert game._stats[StatKey.ALLIES_PLAYED] == 0

    def test_multiple_allies_entering_counted(self, game):
        before = _snap(board=[])
        after  = _snap(board=[_a(Allies.Gondorian_Spearman), _a(Allies.Wandering_Took)])
        game._update_stats(before, after, PhaseKey.PLANNING)
        assert game._stats[StatKey.ALLIES_PLAYED] == 2

    def test_ally_count_only_in_planning_phase(self, game):
        before = _snap(board=[])
        after  = _snap(board=[_a(Allies.Gondorian_Spearman)])
        game._update_stats(before, after, PhaseKey.COMBAT)
        assert game._stats[StatKey.ALLIES_PLAYED] == 0


class TestUpdateStatsCombat:
    def test_enemy_defeated_counted(self, game):
        before = _snap(engaged=[(Enemies.Dol_Guldur_Orcs, 3)])
        after  = _snap(engaged=[])
        game._update_stats(before, after, PhaseKey.COMBAT)
        assert game._stats[StatKey.ENEMIES_DEFEATED] == 1

    def test_multiple_enemies_defeated(self, game):
        before = _snap(engaged=[(Enemies.Dol_Guldur_Orcs, 3), (Enemies.Ungoliants_Spawn, 5)])
        after  = _snap(engaged=[])
        game._update_stats(before, after, PhaseKey.COMBAT)
        assert game._stats[StatKey.ENEMIES_DEFEATED] == 2

    def test_surviving_enemy_not_counted_as_defeated(self, game):
        before = _snap(engaged=[(Enemies.Dol_Guldur_Orcs, 3)])
        after  = _snap(engaged=[(Enemies.Dol_Guldur_Orcs, 1)])
        game._update_stats(before, after, PhaseKey.COMBAT)
        assert game._stats[StatKey.ENEMIES_DEFEATED] == 0

    def test_damage_to_enemy_tracked(self, game):
        before = _snap(engaged=[(Enemies.Dol_Guldur_Orcs, 5)])
        after  = _snap(engaged=[(Enemies.Dol_Guldur_Orcs, 2)])
        game._update_stats(before, after, PhaseKey.COMBAT)
        assert game._stats[StatKey.DAMAGE_TO_ENEMIES] == 3

    def test_damage_on_enemy_kill_tracked(self, game):
        before = _snap(engaged=[(Enemies.Dol_Guldur_Orcs, 4)])
        after  = _snap(engaged=[])
        game._update_stats(before, after, PhaseKey.COMBAT)
        assert game._stats[StatKey.DAMAGE_TO_ENEMIES] == 4

    def test_damage_to_hero_tracked(self, game):
        before = _snap(heroes=[_h(Heroes.Eowyn,   hp=10, max_hp=15)])
        after  = _snap(heroes=[_h(Heroes.Eowyn,   hp=7,  max_hp=15)])
        game._update_stats(before, after, PhaseKey.COMBAT)
        assert game._stats[StatKey.DAMAGE_TO_HEROES] == 3

    def test_hero_death_damage_tracked(self, game):
        before = _snap(heroes=[_h(Heroes.Eleanor, hp=2, max_hp=2)])
        after  = _snap(heroes=[])
        game._update_stats(before, after, PhaseKey.COMBAT)
        assert game._stats[StatKey.DAMAGE_TO_HEROES] == 2

    def test_combat_stats_only_in_combat_phase(self, game):
        before = _snap(engaged=[(Enemies.Dol_Guldur_Orcs, 5)], heroes=[_h(Heroes.Thalin, hp=10, max_hp=10)])
        after  = _snap(engaged=[],                              heroes=[_h(Heroes.Thalin, hp=7,  max_hp=10)])
        game._update_stats(before, after, PhaseKey.QUEST)
        assert game._stats[StatKey.ENEMIES_DEFEATED] == 0
        assert game._stats[StatKey.DAMAGE_TO_HEROES] == 0


class TestUpdateStatsLocations:
    def test_location_cleared_counted(self, game):
        before = _snap(active_loc=Locations.Forest_Gate)
        after  = _snap(active_loc=None)
        game._update_stats(before, after, PhaseKey.QUEST)
        assert game._stats[StatKey.LOCATIONS_FINISHED] == 1

    def test_location_not_cleared_not_counted(self, game):
        before = _snap(active_loc=Locations.Forest_Gate)
        after  = _snap(active_loc=Locations.Forest_Gate)
        game._update_stats(before, after, PhaseKey.QUEST)
        assert game._stats[StatKey.LOCATIONS_FINISHED] == 0

    def test_location_appearing_not_counted(self, game):
        before = _snap(active_loc=None)
        after  = _snap(active_loc=Locations.Forest_Gate)
        game._update_stats(before, after, PhaseKey.TRAVEL)
        assert game._stats[StatKey.LOCATIONS_FINISHED] == 0

    def test_location_cleared_tracked_in_any_phase(self, game):
        before = _snap(active_loc=Locations.Old_Forest_Road)
        after  = _snap(active_loc=None)
        game._update_stats(before, after, PhaseKey.COMBAT)
        assert game._stats[StatKey.LOCATIONS_FINISHED] == 1


class TestLogSummary:
    def test_victory_in_output(self, game, capsys):
        Logger.enable()
        game.log_summary(is_victory=True)
        assert "VICTORY" in capsys.readouterr().out

    def test_defeat_in_output(self, game, capsys):
        Logger.enable()
        game.log_summary(is_victory=False)
        assert "DEFEAT" in capsys.readouterr().out

    def test_round_count_in_output(self, game, capsys):
        Logger.enable()
        game._round = 7
        game.log_summary(is_victory=True)
        assert "7" in capsys.readouterr().out

    def test_stats_values_in_output(self, game, capsys):
        Logger.enable()
        game._stats[StatKey.ENEMIES_DEFEATED] = 5
        game._stats[StatKey.ALLIES_PLAYED] = 3
        game.log_summary(is_victory=True)
        out = capsys.readouterr().out
        assert "5" in out
        assert "3" in out

    def test_summary_not_logged_when_disabled(self, game, capsys):
        game.log_summary(is_victory=True)
        assert capsys.readouterr().out == ""
