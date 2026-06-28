import pytest

from config.limited.cards_list import Heroes, Allies, Enemies, Locations, Quests, Sphere
from config.log_constants import SnapshotKey, StatKey, PhaseKey
from src.logging.logger import Logger
from src.game.logging_game import LoggingGame
from src.game.log_formatters import _HeroSnap, _AllySnap, _HandSnap
from src.cards import Enemy, Location


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


# ── _snapshot ──────────────────────────────────────────────────────────────────


class TestSnapshot:
    def test_contains_all_snapshot_keys(self, game):
        snap = game._snapshot()
        for key in SnapshotKey:
            assert key in snap

    def test_captures_table_threat(self, game):
        game.table.table_threat = 33
        assert game._snapshot()[SnapshotKey.THREAT] == 33

    def test_captures_hero_names(self, game):
        snap = game._snapshot()
        assert Heroes.Eowyn in [h.name for h in snap[SnapshotKey.HEROES]]

    def test_empty_quest_deck_gives_none_quest_fields(self, game):
        game.table.quest_deck = []
        snap = game._snapshot()
        assert snap[SnapshotKey.QUEST_NAME] is None
        assert snap[SnapshotKey.QUEST_PROGRESS] is None

    def test_no_active_location_gives_none(self, game):
        game.table.active_travel_location = None
        assert game._snapshot()[SnapshotKey.ACTIVE_LOC] is None


# ── _diff_planning_resources ───────────────────────────────────────────────────


class TestDiffPlanningResources:
    def test_no_change_returns_false(self, game):
        snap = _snap(heroes=[_h(Heroes.Eowyn, res=2, sphere=Sphere.Spirit)])
        assert game._diff_planning_resources(snap, snap) is False

    def test_change_returns_true(self, game):
        Logger.enable()
        before = _snap(heroes=[_h(Heroes.Eowyn, res=3, sphere=Sphere.Spirit)])
        after  = _snap(heroes=[_h(Heroes.Eowyn, res=1, sphere=Sphere.Spirit)])
        assert game._diff_planning_resources(before, after) is True

    def test_logs_resource_arrow(self, game, capsys):
        Logger.enable()
        before = _snap(heroes=[_h(Heroes.Eowyn, res=3, sphere=Sphere.Spirit)])
        after  = _snap(heroes=[_h(Heroes.Eowyn, res=1, sphere=Sphere.Spirit)])
        game._diff_planning_resources(before, after)
        assert "3->1" in capsys.readouterr().out

    def test_unchanged_sphere_shown_without_arrow(self, game, capsys):
        Logger.enable()
        before = _snap(heroes=[
            _h(Heroes.Eowyn,   res=3, sphere=Sphere.Spirit),
            _h(Heroes.Eleanor, res=1, sphere=Sphere.Tactics),
        ])
        after = _snap(heroes=[
            _h(Heroes.Eowyn,   res=1, sphere=Sphere.Spirit),
            _h(Heroes.Eleanor, res=1, sphere=Sphere.Tactics),
        ])
        game._diff_planning_resources(before, after)
        out = capsys.readouterr().out
        assert "3->1" in out


# ── _diff_heroes ───────────────────────────────────────────────────────────────


class TestDiffHeroes:
    def test_no_change_returns_false(self, game):
        snap = _snap(heroes=[_h(Heroes.Eowyn, hp=5)])
        assert game._diff_heroes(snap, snap, PhaseKey.QUEST) is False

    def test_returns_false_in_planning_phase(self, game):
        before = _snap(heroes=[_h(Heroes.Eowyn, hp=5)])
        after  = _snap(heroes=[_h(Heroes.Eowyn, hp=3)])
        assert game._diff_heroes(before, after, PhaseKey.PLANNING) is False

    def test_hero_death_logged(self, game, capsys):
        Logger.enable()
        before = _snap(heroes=[_h(Heroes.Eowyn)])
        after  = _snap(heroes=[])
        result = game._diff_heroes(before, after, PhaseKey.COMBAT)
        assert result is True
        assert "DIED" in capsys.readouterr().out

    def test_hero_stat_change_logged(self, game, capsys):
        Logger.enable()
        before = _snap(heroes=[_h(Heroes.Eowyn, hp=5)])
        after  = _snap(heroes=[_h(Heroes.Eowyn, hp=3)])
        result = game._diff_heroes(before, after, PhaseKey.COMBAT)
        assert result is True
        assert "hp" in capsys.readouterr().out


# ── _diff_board ────────────────────────────────────────────────────────────────


class TestDiffBoard:
    def test_no_change_returns_false(self, game):
        snap = _snap(board=[_a(Allies.Gondorian_Spearman)])
        assert game._diff_board(snap, snap, PhaseKey.QUEST) is False

    def test_ally_death_logged(self, game, capsys):
        Logger.enable()
        before = _snap(board=[_a(Allies.Gondorian_Spearman)])
        after  = _snap(board=[])
        result = game._diff_board(before, after, PhaseKey.COMBAT)
        assert result is True
        assert "died" in capsys.readouterr().out

    def test_planning_phase_shows_new_marker(self, game, capsys):
        Logger.enable()
        before = _snap(board=[])
        after  = _snap(board=[_a(Allies.Gondorian_Spearman)])
        result = game._diff_board(before, after, PhaseKey.PLANNING)
        assert result is True
        assert "New!" in capsys.readouterr().out

    def test_non_planning_phase_shows_hp_diff(self, game, capsys):
        Logger.enable()
        before = _snap(board=[_a(Allies.Gondorian_Spearman, hp=2)])
        after  = _snap(board=[_a(Allies.Gondorian_Spearman, hp=1)])
        result = game._diff_board(before, after, PhaseKey.COMBAT)
        assert result is True
        assert "hp" in capsys.readouterr().out


# ── _diff_hand ─────────────────────────────────────────────────────────────────


class TestDiffHand:
    def test_no_change_returns_false(self, game):
        snap = _snap(hand=[_HandSnap(Allies.Gondorian_Spearman, 2)])
        assert game._diff_hand(snap, snap) is False

    def test_new_card_logged_with_new_marker(self, game, capsys):
        Logger.enable()
        before = _snap(hand=[])
        after  = _snap(hand=[_HandSnap(Allies.Gondorian_Spearman, 2)])
        result = game._diff_hand(before, after)
        assert result is True
        assert "New!" in capsys.readouterr().out

    def test_empty_hand_logs_empty(self, game, capsys):
        Logger.enable()
        before = _snap(hand=[_HandSnap(Allies.Gondorian_Spearman, 2)])
        after  = _snap(hand=[])
        result = game._diff_hand(before, after)
        assert result is True
        assert "empty" in capsys.readouterr().out


# ── _diff_threat ───────────────────────────────────────────────────────────────


class TestDiffThreat:
    def test_no_change_returns_false(self, game):
        snap = _snap(threat=30)
        assert game._diff_threat(snap, snap) is False

    def test_threat_change_logged(self, game, capsys):
        Logger.enable()
        before = _snap(threat=25)
        after  = _snap(threat=26)
        result = game._diff_threat(before, after)
        assert result is True
        assert "25" in capsys.readouterr().out


# ── _diff_quest ────────────────────────────────────────────────────────────────


class TestDiffQuest:
    def test_no_change_returns_false(self, game):
        snap = _snap(quest_name=Quests.Flies_and_Spiders, quest_progress=2, quest_required=5)
        assert game._diff_quest(snap, snap) is False

    def test_no_quest_before_returns_false(self, game):
        before = _snap(quest_name=None)
        after  = _snap(quest_name=Quests.Flies_and_Spiders, quest_progress=0, quest_required=5)
        assert game._diff_quest(before, after) is False

    def test_quest_completion_logged(self, game, capsys):
        Logger.enable()
        before = _snap(quest_name=Quests.Flies_and_Spiders,   quest_progress=5, quest_required=5)
        after  = _snap(quest_name=Quests.A_fork_in_the_road,  quest_progress=0, quest_required=8)
        result = game._diff_quest(before, after)
        assert result is True
        assert "completed" in capsys.readouterr().out

    def test_quest_completion_with_overflow_logged(self, game, capsys):
        Logger.enable()
        before = _snap(quest_name=Quests.Flies_and_Spiders,  quest_progress=5, quest_required=5)
        after  = _snap(quest_name=Quests.A_fork_in_the_road, quest_progress=2, quest_required=8)
        result = game._diff_quest(before, after)
        assert result is True
        assert "carry over" in capsys.readouterr().out

    def test_progress_increase_logged(self, game, capsys):
        Logger.enable()
        before = _snap(quest_name=Quests.Flies_and_Spiders, quest_progress=2, quest_required=5)
        after  = _snap(quest_name=Quests.Flies_and_Spiders, quest_progress=4, quest_required=5)
        result = game._diff_quest(before, after)
        assert result is True
        out = capsys.readouterr().out
        assert "2" in out and "4" in out


# ── _diff_location ─────────────────────────────────────────────────────────────


class TestDiffLocation:
    def test_no_change_returns_false(self, game):
        snap = _snap(active_loc=None)
        assert game._diff_location(snap, snap) is False

    def test_progress_on_active_location_logged(self, game, capsys):
        Logger.enable()
        before = _snap(active_loc=Locations.Forest_Gate, active_loc_progress=1)
        after  = _snap(active_loc=Locations.Forest_Gate, active_loc_progress=3)
        result = game._diff_location(before, after)
        assert result is True
        assert "1" in capsys.readouterr().out

    def test_location_cleared_logged(self, game, capsys):
        Logger.enable()
        before = _snap(active_loc=Locations.Forest_Gate, active_loc_progress=3)
        after  = _snap(active_loc=None, active_loc_progress=None)
        result = game._diff_location(before, after)
        assert result is True
        assert "cleared" in capsys.readouterr().out

    def test_new_active_location_logged(self, game, capsys):
        Logger.enable()
        before = _snap(active_loc=None)
        after  = _snap(active_loc=Locations.Forest_Gate, active_loc_progress=0)
        result = game._diff_location(before, after)
        assert result is True
        assert "active location" in capsys.readouterr().out


# ── _diff_staging ──────────────────────────────────────────────────────────────


class TestDiffStaging:
    def test_no_change_returns_false(self, game):
        snap = _snap(staging=[Enemies.Dol_Guldur_Orcs])
        assert game._diff_staging(snap, snap) is False

    def test_new_card_in_staging_logged(self, game, capsys):
        Logger.enable()
        before = _snap(staging=[])
        after  = _snap(staging=[Enemies.Dol_Guldur_Orcs])
        result = game._diff_staging(before, after)
        assert result is True
        assert "revealed" in capsys.readouterr().out

    def test_card_removed_from_staging_logged(self, game, capsys):
        Logger.enable()
        before = _snap(staging=[Enemies.Dol_Guldur_Orcs])
        after  = _snap(staging=[])
        result = game._diff_staging(before, after)
        assert result is True
        assert "removed" in capsys.readouterr().out

    def test_duplicate_cards_show_x2_count(self, game, capsys):
        Logger.enable()
        before = _snap(staging=[])
        after  = _snap(staging=[Enemies.Dol_Guldur_Orcs, Enemies.Dol_Guldur_Orcs])
        result = game._diff_staging(before, after)
        assert result is True
        assert "x2" in capsys.readouterr().out


# ── _diff_engaged ──────────────────────────────────────────────────────────────


class TestDiffEngaged:
    def test_no_change_returns_false(self, game):
        snap = _snap(engaged=[(Enemies.Dol_Guldur_Orcs, 3)])
        assert game._diff_engaged(snap, snap) is False

    def test_new_engagement_logged(self, game, capsys):
        Logger.enable()
        before = _snap(engaged=[])
        after  = _snap(engaged=[(Enemies.Dol_Guldur_Orcs, 3)])
        result = game._diff_engaged(before, after)
        assert result is True
        assert "engaged" in capsys.readouterr().out

    def test_enemy_defeated_logged(self, game, capsys):
        Logger.enable()
        before = _snap(engaged=[(Enemies.Dol_Guldur_Orcs, 3)])
        after  = _snap(engaged=[])
        result = game._diff_engaged(before, after)
        assert result is True
        assert "defeated" in capsys.readouterr().out

    def test_hp_decrease_logged(self, game, capsys):
        Logger.enable()
        before = _snap(engaged=[(Enemies.Dol_Guldur_Orcs, 5)])
        after  = _snap(engaged=[(Enemies.Dol_Guldur_Orcs, 2)])
        result = game._diff_engaged(before, after)
        assert result is True
        assert "hp" in capsys.readouterr().out


# ── _log_travel_state ──────────────────────────────────────────────────────────


class TestLogTravelState:
    def test_with_active_location(self, game, capsys):
        Logger.enable()
        game.table.active_travel_location = Location(Locations.Forest_Gate, threat=2, required_progress=4)
        game._log_travel_state()
        assert "Forest_Gate" in capsys.readouterr().out

    def test_without_active_location(self, game, capsys):
        Logger.enable()
        game.table.active_travel_location = None
        game._log_travel_state()
        assert "none" in capsys.readouterr().out


# ── _log_combat_state ──────────────────────────────────────────────────────────


class TestLogCombatState:
    def test_empty_staging_and_engagement(self, game, capsys):
        Logger.enable()
        game.table.encounter_staging = []
        game.table.encounter_engagement = []
        game._log_combat_state()
        out = capsys.readouterr().out
        assert "empty" in out
        assert "none" in out

    def test_shows_engaged_enemy_stats(self, game, capsys):
        Logger.enable()
        enemy = Enemy(Enemies.Dol_Guldur_Orcs, attack=2, defense=0, max_hit_points=3, engagement=15, threat=2)
        game.table.encounter_engagement = [enemy]
        game.table.encounter_staging = []
        game._log_combat_state()
        assert "atk=2" in capsys.readouterr().out

    def test_shows_staging_enemy(self, game, capsys):
        Logger.enable()
        enemy = Enemy(Enemies.Dol_Guldur_Orcs, attack=2, defense=0, max_hit_points=3, engagement=25, threat=2)
        game.table.encounter_staging = [enemy]
        game.table.encounter_engagement = []
        game._log_combat_state()
        assert "enemy" in capsys.readouterr().out

    def test_shows_staging_location(self, game, capsys):
        Logger.enable()
        loc = Location(Locations.Forest_Gate, threat=2, required_progress=4)
        game.table.encounter_staging = [loc]
        game.table.encounter_engagement = []
        game._log_combat_state()
        assert "location" in capsys.readouterr().out


# ── _log_encounter_state ───────────────────────────────────────────────────────


class TestLogEncounterState:
    def test_enemy_revealed_to_staging(self, game, capsys):
        Logger.enable()
        game.table.table_threat = 20
        enemy = Enemy(Enemies.Dol_Guldur_Orcs, attack=2, defense=0, max_hit_points=3, engagement=30, threat=2)
        game.table.encounter_staging = [enemy]
        game.table.encounter_engagement = []
        game._log_encounter_state(_snap(staging=[], engaged=[]), _snap())
        out = capsys.readouterr().out
        assert "revealed" in out and "staging" in out

    def test_enemy_auto_engaged(self, game, capsys):
        Logger.enable()
        game.table.table_threat = 30
        enemy = Enemy(Enemies.Dol_Guldur_Orcs, attack=2, defense=0, max_hit_points=3, engagement=15, threat=2)
        game.table.encounter_staging = []
        game.table.encounter_engagement = [enemy]
        game._log_encounter_state(_snap(staging=[], engaged=[]), _snap())
        assert "auto-engaged" in capsys.readouterr().out

    def test_enemy_engaged_from_staging_forced(self, game, capsys):
        Logger.enable()
        game.table.table_threat = 30
        enemy = Enemy(Enemies.Dol_Guldur_Orcs, attack=2, defense=0, max_hit_points=3, engagement=15, threat=2)
        game.table.encounter_staging = []
        game.table.encounter_engagement = [enemy]
        game._log_encounter_state(_snap(staging=[Enemies.Dol_Guldur_Orcs], engaged=[]), _snap())
        assert "forced" in capsys.readouterr().out

    def test_enemy_engaged_from_staging_optional(self, game, capsys):
        Logger.enable()
        game.table.table_threat = 20
        enemy = Enemy(Enemies.Dol_Guldur_Orcs, attack=2, defense=0, max_hit_points=3, engagement=30, threat=2)
        game.table.encounter_staging = []
        game.table.encounter_engagement = [enemy]
        game._log_encounter_state(_snap(staging=[Enemies.Dol_Guldur_Orcs], engaged=[]), _snap())
        assert "optional" in capsys.readouterr().out

    def test_location_revealed_to_staging(self, game, capsys):
        Logger.enable()
        game.table.table_threat = 20
        loc = Location(Locations.Forest_Gate, threat=2, required_progress=4)
        game.table.encounter_staging = [loc]
        game.table.encounter_engagement = []
        game._log_encounter_state(_snap(staging=[], engaged=[]), _snap())
        assert "location" in capsys.readouterr().out


# ── log_summary (elif branch) ──────────────────────────────────────────────────


class TestLogSummaryThreatDefeat:
    def test_threat_defeat_branch_logged(self, game, capsys):
        Logger.enable()
        game.table.table_threat = 50
        game.log_summary(is_victory=False)
        assert "Threat" in capsys.readouterr().out


# ── _fmt_quest ─────────────────────────────────────────────────────────────────


class TestFmtQuest:
    def test_empty_quest_deck_returns_completed(self, game):
        game.table.quest_deck = []
        assert game._fmt_quest() == "all completed!"

    def test_quest_without_location_shows_progress(self, game):
        game.table.active_travel_location = None
        assert "/" in game._fmt_quest()

    def test_quest_with_active_location_shows_location_info(self, game):
        game.table.active_travel_location = Location(Locations.Forest_Gate, threat=2, required_progress=4)
        assert "location" in game._fmt_quest()


# ── _log_diff ──────────────────────────────────────────────────────────────────


class TestLogDiff:
    def test_no_changes_logs_no_changes_message(self, game, capsys):
        Logger.enable()
        snap = game._snapshot()
        game._log_diff(snap, "ResourcesPhase")
        assert "no changes" in capsys.readouterr().out

    def test_travel_phase_logs_active_location_line(self, game, capsys):
        Logger.enable()
        game.table.active_travel_location = None
        snap = game._snapshot()
        game._log_diff(snap, PhaseKey.TRAVEL)
        assert "Active location" in capsys.readouterr().out

    def test_combat_phase_logs_engaged_section(self, game, capsys):
        Logger.enable()
        game.table.encounter_staging = []
        game.table.encounter_engagement = []
        snap = game._snapshot()
        game._log_diff(snap, PhaseKey.COMBAT)
        assert "Engaged" in capsys.readouterr().out

    def test_encounter_phase_logs_auto_engaged_enemy(self, game, capsys):
        Logger.enable()
        game.table.table_threat = 30
        enemy = Enemy(Enemies.Dol_Guldur_Orcs, attack=2, defense=0, max_hit_points=3, engagement=15, threat=2)
        snap = _snap(staging=[], engaged=[])
        game.table.encounter_staging = []
        game.table.encounter_engagement = [enemy]
        game._log_diff(snap, PhaseKey.ENCOUNTER)
        assert "auto-engaged" in capsys.readouterr().out
