from collections import Counter
from enum import StrEnum
from typing import NamedTuple

from src.game.game import Game
from logger import Logger


def _name(x) -> str:
    """Convert a card object, Enum value, or fallback string to a display name."""
    if isinstance(x, str):
        return x
    n = x.name
    if isinstance(n, str):
        return n
    return n.name if hasattr(n, "name") else str(n)


class _HeroSnap(NamedTuple):
    name:      object
    hp:        int
    max_hp:    int
    res:       int
    exhausted: bool
    sphere:    object


class _AllySnap(NamedTuple):
    name:      object
    hp:        int
    max_hp:    int
    exhausted: bool


class _PhaseKey(StrEnum):
    RESOURCES = "ResourcesPhase"
    PLANNING  = "PlanningPhase"
    QUEST     = "QuestPhase"
    TRAVEL    = "TravelPhase"
    ENCOUNTER = "EncounterPhase"
    COMBAT    = "CombatPhase"
    REFRESH   = "RefreshPhase"


class _StatKey(StrEnum):
    RESOURCES_GENERATED = "resources_generated"
    RESOURCES_SPENT     = "resources_spent"
    ALLIES_PLAYED       = "allies_played"
    ENEMIES_DEFEATED    = "enemies_defeated"
    DAMAGE_TO_ENEMIES   = "damage_to_enemies"
    DAMAGE_TO_HEROES    = "damage_to_heroes"
    LOCATIONS_FINISHED  = "locations_finished"


class _SnapshotKey(StrEnum):
    THREAT              = "threat"
    HEROES              = "heroes"
    BOARD               = "board"
    STAGING             = "staging"
    ENGAGED             = "engaged"
    HAND                = "hand"
    QUEST_NAME          = "quest_name"
    QUEST_PROGRESS      = "quest_progress"
    QUEST_REQUIRED      = "quest_required"
    ACTIVE_LOC          = "active_loc"
    ACTIVE_LOC_PROGRESS = "active_loc_progress"
    TOTAL_RESOURCES     = "total_resources"


_SEP       = "=" * 60
_DASH      = "-" * 60
_NEW_MARKER = "  # New!"


class _CardState(StrEnum):
    EXHAUSTED = "exhausted"
    READY     = "ready"


def _fmt_hero(snap: _HeroSnap) -> str:
    state = _CardState.EXHAUSTED if snap.exhausted else _CardState.READY
    return f"{_name(snap.name)} [{_name(snap.sphere)}] hp={snap.hp}/{snap.max_hp} res={snap.res} {state}"


def _fmt_ally(snap: _AllySnap, new: bool = False) -> str:
    state  = _CardState.EXHAUSTED if snap.exhausted else _CardState.READY
    suffix = _NEW_MARKER if new else ""
    return f"{_name(snap.name)} hp={snap.hp}/{snap.max_hp} {state}{suffix}"


class LoggingGame(Game):
    """Subclass of Game that prints a detailed log of every round and phase."""

    def __init__(self, agent=None):
        super().__init__(agent=agent)
        self._round = 0
        self._stats = {
            _StatKey.RESOURCES_GENERATED: 0,
            _StatKey.RESOURCES_SPENT:     0,
            _StatKey.ALLIES_PLAYED:       0,
            _StatKey.ENEMIES_DEFEATED:    0,
            _StatKey.DAMAGE_TO_ENEMIES:   0,
            _StatKey.DAMAGE_TO_HEROES:    0,
            _StatKey.LOCATIONS_FINISHED:  0,
        }

    def run_round(self) -> None:
        self._round += 1
        Logger.log(f"\n{_SEP}")
        Logger.log(f"  ROUND {self._round}")
        Logger.log(f"  Threat:  {self.table.table_threat}/50")
        Logger.log(f"  Quest:   {self._fmt_quest()}")
        if not self.table.player_heroes:
            Logger.log(f"  Heroes:  all dead")
        else:
            Logger.log(f"  Heroes:")
            for h in self.table.player_heroes:
                snap = _HeroSnap(h.name, h.hit_points, h.max_hit_points,
                                 h.resource_pool, h.exhausted, h.sphere_of_influence)
                Logger.log(f"    {_fmt_hero(snap)}")
        Logger.log(f"  Board:   {self._fmt_board()}")
        Logger.log(f"  Hand:    {self._fmt_hand()}")
        Logger.log(f"  Staging: {self._fmt_staging()}")
        Logger.log(f"  Engaged: {self._fmt_engaged()}")

        for phase in self.phases:
            if self.table.check_win_condition() or self.table.check_lose_condition():
                return
            before = self._snapshot()
            phase_name = phase.__class__.__name__
            Logger.log(f"\n  -- {phase_name} --")
            phase.execute()
            self._log_diff(before, phase_name)

    # ── Snapshot ──────────────────────────────────────────────────

    def _snapshot(self) -> dict:
        return {
            _SnapshotKey.THREAT:              self.table.table_threat,
            _SnapshotKey.HEROES:              [
                _HeroSnap(h.name, h.hit_points, h.max_hit_points,
                          h.resource_pool, h.exhausted, h.sphere_of_influence)
                for h in self.table.player_heroes
            ],
            _SnapshotKey.BOARD:               [
                _AllySnap(a.name, a.hit_points, a.max_hit_points, a.exhausted)
                for a in self.table.player_board
            ],
            _SnapshotKey.STAGING:             [c.name for c in self.table.encounter_staging],
            _SnapshotKey.ENGAGED:             [(e.name, e.hit_points) for e in self.table.encounter_engagement],
            _SnapshotKey.HAND:                [c.name for c in self.table.player_hand],
            _SnapshotKey.QUEST_NAME:          self.table.quest_deck[0].name if self.table.quest_deck else None,
            _SnapshotKey.QUEST_PROGRESS:      self.table.quest_deck[0].progress if self.table.quest_deck else None,
            _SnapshotKey.QUEST_REQUIRED:      self.table.quest_deck[0].required_progress if self.table.quest_deck else None,
            _SnapshotKey.ACTIVE_LOC:          self.table.active_travel_location.name if self.table.active_travel_location else None,
            _SnapshotKey.ACTIVE_LOC_PROGRESS: self.table.active_travel_location.progress if self.table.active_travel_location else None,
            _SnapshotKey.TOTAL_RESOURCES:     sum(h.resource_pool for h in self.table.player_heroes),
        }

    # ── Diff ──────────────────────────────────────────────────────

    def _log_diff(self, before: dict, phase_name: str = "") -> None:
        after = self._snapshot()
        self._update_stats(before, after, phase_name)
        any_change = False

        # Heroes
        before_hero_map = {s.name: s for s in before[_SnapshotKey.HEROES]}
        after_hero_map  = {s.name: s for s in after[_SnapshotKey.HEROES]}
        if before_hero_map != after_hero_map:
            any_change = True
            for name in before_hero_map:
                if name not in after_hero_map:
                    Logger.log(f"    -> {_name(name)} DIED")
            if after_hero_map:
                Logger.log(f"    -> Heroes:")
                for snap in after[_SnapshotKey.HEROES]:
                    Logger.log(f"         {_fmt_hero(snap)}")

        # Board (allies)
        before_ally_map = {s.name: s for s in before[_SnapshotKey.BOARD]}
        after_ally_map  = {s.name: s for s in after[_SnapshotKey.BOARD]}
        if before_ally_map != after_ally_map:
            any_change = True
            for name in before_ally_map:
                if name not in after_ally_map:
                    Logger.log(f"    -> ally {_name(name)} died")
            Logger.log(f"    -> Board:")
            if after_ally_map:
                for snap in after[_SnapshotKey.BOARD]:
                    Logger.log(f"         {_fmt_ally(snap, new=snap.name not in before_ally_map)}")
            else:
                Logger.log(f"         (empty)")

        # Hand
        before_hand = before[_SnapshotKey.HAND]
        after_hand  = after[_SnapshotKey.HAND]
        if before_hand != after_hand:
            any_change = True
            Logger.log(f"    -> Hand: {[_name(n) for n in after_hand]}")

        # Threat
        if after[_SnapshotKey.THREAT] != before[_SnapshotKey.THREAT]:
            any_change = True
            Logger.log(f"    -> threat: {before[_SnapshotKey.THREAT]} -> {after[_SnapshotKey.THREAT]}")

        # Quest
        if after[_SnapshotKey.QUEST_NAME] != before[_SnapshotKey.QUEST_NAME]:
            if before[_SnapshotKey.QUEST_NAME]:
                any_change = True
                after_qn = _name(after[_SnapshotKey.QUEST_NAME]) if after[_SnapshotKey.QUEST_NAME] else "END"
                Logger.log(f"    -> quest completed: {_name(before[_SnapshotKey.QUEST_NAME])} -> {after_qn}")
        elif after[_SnapshotKey.QUEST_PROGRESS] != before[_SnapshotKey.QUEST_PROGRESS] and after[_SnapshotKey.QUEST_PROGRESS] is not None:
            any_change = True
            Logger.log(f"    -> quest progress: {before[_SnapshotKey.QUEST_PROGRESS]} -> {after[_SnapshotKey.QUEST_PROGRESS]}/{after[_SnapshotKey.QUEST_REQUIRED]}")

        # Location
        if before[_SnapshotKey.ACTIVE_LOC] and before[_SnapshotKey.ACTIVE_LOC] == after[_SnapshotKey.ACTIVE_LOC]:
            if after[_SnapshotKey.ACTIVE_LOC_PROGRESS] != before[_SnapshotKey.ACTIVE_LOC_PROGRESS]:
                any_change = True
                Logger.log(f"    -> location {_name(before[_SnapshotKey.ACTIVE_LOC])} progress: {before[_SnapshotKey.ACTIVE_LOC_PROGRESS]} -> {after[_SnapshotKey.ACTIVE_LOC_PROGRESS]}")
        if before[_SnapshotKey.ACTIVE_LOC] and not after[_SnapshotKey.ACTIVE_LOC]:
            any_change = True
            Logger.log(f"    -> location cleared: {_name(before[_SnapshotKey.ACTIVE_LOC])}")
        if not before[_SnapshotKey.ACTIVE_LOC] and after[_SnapshotKey.ACTIVE_LOC]:
            any_change = True
            Logger.log(f"    -> active location: {_name(after[_SnapshotKey.ACTIVE_LOC])}")

        # Staging
        before_staging = Counter(before[_SnapshotKey.STAGING])
        after_staging  = Counter(after[_SnapshotKey.STAGING])
        for name, count in (after_staging - before_staging).items():
            any_change = True
            label = f"revealed: {_name(name)}"
            Logger.log(f"    -> {label} x{count}" if count > 1 else f"    -> {label}")
        for name, count in (before_staging - after_staging).items():
            any_change = True
            label = f"removed from staging: {_name(name)}"
            Logger.log(f"    -> {label} x{count}" if count > 1 else f"    -> {label}")

        # Engaged
        before_engaged = dict(before[_SnapshotKey.ENGAGED])
        after_engaged  = dict(after[_SnapshotKey.ENGAGED])
        for name in after_engaged:
            if name not in before_engaged:
                any_change = True
                Logger.log(f"    -> engaged: {_name(name)} (hp {after_engaged[name]})")
        for name, hp in before_engaged.items():
            if name not in after_engaged:
                any_change = True
                Logger.log(f"    -> enemy defeated: {_name(name)}")
            elif after_engaged[name] != hp:
                any_change = True
                Logger.log(f"    -> {_name(name)} hp: {hp} -> {after_engaged[name]}")

        if not any_change:
            Logger.log(f"    -> (no changes)")

    # ── Stats ─────────────────────────────────────────────────────

    def _update_stats(self, before: dict, after: dict, phase_name: str) -> None:
        if phase_name == _PhaseKey.RESOURCES:
            delta = after[_SnapshotKey.TOTAL_RESOURCES] - before[_SnapshotKey.TOTAL_RESOURCES]
            if delta > 0:
                self._stats[_StatKey.RESOURCES_GENERATED] += delta

        if phase_name == _PhaseKey.PLANNING:
            delta = before[_SnapshotKey.TOTAL_RESOURCES] - after[_SnapshotKey.TOTAL_RESOURCES]
            if delta > 0:
                self._stats[_StatKey.RESOURCES_SPENT] += delta
            before_names = Counter(s.name for s in before[_SnapshotKey.BOARD])
            after_names  = Counter(s.name for s in after[_SnapshotKey.BOARD])
            self._stats[_StatKey.ALLIES_PLAYED] += sum((after_names - before_names).values())

        if phase_name == _PhaseKey.COMBAT:
            before_engaged = dict(before[_SnapshotKey.ENGAGED])
            after_engaged  = dict(after[_SnapshotKey.ENGAGED])
            for name, hp in before_engaged.items():
                after_hp = after_engaged.get(name, 0)
                if name not in after_engaged:
                    self._stats[_StatKey.ENEMIES_DEFEATED] += 1
                self._stats[_StatKey.DAMAGE_TO_ENEMIES] += hp - after_hp

            before_hero_map = {s.name: s for s in before[_SnapshotKey.HEROES]}
            after_hero_map  = {s.name: s for s in after[_SnapshotKey.HEROES]}
            for name, snap in before_hero_map.items():
                after_snap = after_hero_map.get(name)
                after_hp   = after_snap.hp if after_snap else 0
                if after_hp < snap.hp:
                    self._stats[_StatKey.DAMAGE_TO_HEROES] += snap.hp - after_hp

        if before[_SnapshotKey.ACTIVE_LOC] and not after[_SnapshotKey.ACTIVE_LOC]:
            self._stats[_StatKey.LOCATIONS_FINISHED] += 1

    # ── Summary ───────────────────────────────────────────────────

    def log_summary(self, is_victory: bool) -> None:
        outcome = "VICTORY" if is_victory else "DEFEAT"
        Logger.log(f"\n{_SEP}")
        Logger.log(f"  GAME STATISTICS")
        Logger.log(_SEP)
        Logger.log(f"  >>> {outcome} <<<")
        Logger.log(_DASH)
        Logger.log(f"  Rounds:               {self._round}")
        Logger.log(f"  Heroes alive:         {len(self.table.player_heroes)}")
        Logger.log(f"  Final threat:         {self.table.table_threat}")
        Logger.log(_DASH)
        Logger.log(f"  Resources generated:  {self._stats[_StatKey.RESOURCES_GENERATED]}")
        Logger.log(f"  Resources spent:      {self._stats[_StatKey.RESOURCES_SPENT]}")
        Logger.log(f"  Allies played:        {self._stats[_StatKey.ALLIES_PLAYED]}")
        Logger.log(f"  Enemies defeated:     {self._stats[_StatKey.ENEMIES_DEFEATED]}")
        Logger.log(f"  Locations cleared:    {self._stats[_StatKey.LOCATIONS_FINISHED]}")
        Logger.log(f"  Damage dealt:         {self._stats[_StatKey.DAMAGE_TO_ENEMIES]}")
        Logger.log(f"  Damage received:      {self._stats[_StatKey.DAMAGE_TO_HEROES]}")
        Logger.log(_SEP)

    # ── Formatters ────────────────────────────────────────────────

    def _fmt_quest(self) -> str:
        if not self.table.quest_deck:
            return "all completed!"
        q = self.table.quest_deck[0]
        loc = self.table.active_travel_location
        loc_str = f"  |  location: {_name(loc)} ({loc.progress}/{loc.required_progress})" if loc else ""
        return f"{_name(q)} ({q.progress}/{q.required_progress}){loc_str}"

    def _fmt_board(self) -> str:
        if not self.table.player_board:
            return "empty"
        return "  ".join(
            _fmt_ally(_AllySnap(a.name, a.hit_points, a.max_hit_points, a.exhausted))
            for a in self.table.player_board
        )

    def _fmt_hand(self) -> str:
        if not self.table.player_hand:
            return "[]"
        return str([_name(c.name) for c in self.table.player_hand])

    def _fmt_staging(self) -> str:
        if not self.table.encounter_staging:
            return "empty"
        return "  ".join(_name(c) for c in self.table.encounter_staging)

    def _fmt_engaged(self) -> str:
        if not self.table.encounter_engagement:
            return "none"
        return "  ".join(f"{_name(e)} hp={e.hit_points}" for e in self.table.encounter_engagement)
