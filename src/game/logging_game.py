from collections import Counter
from enum import StrEnum

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


class _SnapshotKey(StrEnum):
    THREAT              = "threat"
    HEROES              = "heroes"
    BOARD               = "board"
    STAGING             = "staging"
    ENGAGED             = "engaged"
    HAND_SIZE           = "hand_size"
    QUEST_NAME          = "quest_name"
    QUEST_PROGRESS      = "quest_progress"
    QUEST_REQUIRED      = "quest_required"
    ACTIVE_LOC          = "active_loc"
    ACTIVE_LOC_PROGRESS = "active_loc_progress"


class LoggingGame(Game):
    """Subclass of Game that prints a detailed log of every round and phase."""

    def __init__(self, agent=None):
        super().__init__(agent=agent)
        self._round = 0

    def run_round(self) -> None:
        self._round += 1
        Logger.log(f"\n{'=' * 60}")
        Logger.log(f"  RUNDA {self._round}")
        Logger.log(f"  Threat:  {self.table.table_threat}/50")
        Logger.log(f"  Quest:   {self._fmt_quest()}")
        Logger.log(f"  Heroes:  {self._fmt_heroes()}")
        Logger.log(f"  Board:   {self._fmt_board()}")
        Logger.log(f"  Staging: {self._fmt_staging()}")
        Logger.log(f"  Engaged: {self._fmt_engaged()}")

        for phase in self.phases:
            if self.table.check_win_condition() or self.table.check_lose_condition():
                return
            before = self._snapshot()
            Logger.log(f"\n  -- {phase.__class__.__name__} --")
            phase.execute()
            self._log_diff(before)

    # ── Snapshot & diff ───────────────────────────────────────────

    def _snapshot(self) -> dict:
        return {
            _SnapshotKey.THREAT:              self.table.table_threat,
            _SnapshotKey.HEROES:              [(h.name, h.hit_points) for h in self.table.player_heroes],
            _SnapshotKey.BOARD:               [(a.name, a.hit_points) for a in self.table.player_board],
            _SnapshotKey.STAGING:             [c.name for c in self.table.encounter_staging],
            _SnapshotKey.ENGAGED:             [(e.name, e.hit_points) for e in self.table.encounter_engagement],
            _SnapshotKey.HAND_SIZE:           len(self.table.player_hand),
            _SnapshotKey.QUEST_NAME:          self.table.quest_deck[0].name if self.table.quest_deck else None,
            _SnapshotKey.QUEST_PROGRESS:      self.table.quest_deck[0].progress if self.table.quest_deck else None,
            _SnapshotKey.QUEST_REQUIRED:      self.table.quest_deck[0].required_progress if self.table.quest_deck else None,
            _SnapshotKey.ACTIVE_LOC:          self.table.active_travel_location.name if self.table.active_travel_location else None,
            _SnapshotKey.ACTIVE_LOC_PROGRESS: self.table.active_travel_location.progress if self.table.active_travel_location else None,
        }

    def _log_diff(self, before: dict) -> None:
        after = self._snapshot()
        changes = []

        if after[_SnapshotKey.THREAT] != before[_SnapshotKey.THREAT]:
            changes.append(f"threat: {before[_SnapshotKey.THREAT]} ->{after[_SnapshotKey.THREAT]}")

        if after[_SnapshotKey.QUEST_NAME] != before[_SnapshotKey.QUEST_NAME]:
            if before[_SnapshotKey.QUEST_NAME]:
                after_qn = _name(after[_SnapshotKey.QUEST_NAME]) if after[_SnapshotKey.QUEST_NAME] else "KONIEC"
                changes.append(f"quest ukończony: {_name(before[_SnapshotKey.QUEST_NAME])} ->{after_qn}")
        elif after[_SnapshotKey.QUEST_PROGRESS] != before[_SnapshotKey.QUEST_PROGRESS] and after[_SnapshotKey.QUEST_PROGRESS] is not None:
            changes.append(f"quest progress: {before[_SnapshotKey.QUEST_PROGRESS]} ->{after[_SnapshotKey.QUEST_PROGRESS]}/{after[_SnapshotKey.QUEST_REQUIRED]}")

        if before[_SnapshotKey.ACTIVE_LOC] and before[_SnapshotKey.ACTIVE_LOC] == after[_SnapshotKey.ACTIVE_LOC]:
            if after[_SnapshotKey.ACTIVE_LOC_PROGRESS] != before[_SnapshotKey.ACTIVE_LOC_PROGRESS]:
                changes.append(f"lokacja {_name(before[_SnapshotKey.ACTIVE_LOC])} progress: {before[_SnapshotKey.ACTIVE_LOC_PROGRESS]} ->{after[_SnapshotKey.ACTIVE_LOC_PROGRESS]}")
        if before[_SnapshotKey.ACTIVE_LOC] and not after[_SnapshotKey.ACTIVE_LOC]:
            changes.append(f"lokacja ukończona: {_name(before[_SnapshotKey.ACTIVE_LOC])}")
        if not before[_SnapshotKey.ACTIVE_LOC] and after[_SnapshotKey.ACTIVE_LOC]:
            changes.append(f"aktywna lokacja: {_name(after[_SnapshotKey.ACTIVE_LOC])}")

        before_heroes = dict(before[_SnapshotKey.HEROES])
        after_heroes  = dict(after[_SnapshotKey.HEROES])
        for name, hp in before_heroes.items():
            if name not in after_heroes:
                changes.append(f"{_name(name)} ZGINĄŁ")
            elif after_heroes[name] != hp:
                changes.append(f"{_name(name)} hp: {hp} ->{after_heroes[name]}")

        before_board = dict(before[_SnapshotKey.BOARD])
        after_board  = dict(after[_SnapshotKey.BOARD])
        for name, hp in before_board.items():
            if name not in after_board:
                changes.append(f"sojusznik {_name(name)} zginął")
            elif after_board[name] != hp:
                changes.append(f"sojusznik {_name(name)} hp: {hp} ->{after_board[name]}")
        for name in after_board:
            if name not in before_board:
                changes.append(f"sojusznik {_name(name)} wchodzi na planszę")

        before_staging = Counter(before[_SnapshotKey.STAGING])
        after_staging  = Counter(after[_SnapshotKey.STAGING])
        for name, count in (after_staging - before_staging).items():
            label = f"ujawniono: {_name(name)}"
            changes.append(f"{label} x{count}" if count > 1 else label)
        for name, count in (before_staging - after_staging).items():
            label = f"usunięto ze staging: {_name(name)}"
            changes.append(f"{label} x{count}" if count > 1 else label)

        before_engaged = dict(before[_SnapshotKey.ENGAGED])
        after_engaged  = dict(after[_SnapshotKey.ENGAGED])
        for name in after_engaged:
            if name not in before_engaged:
                changes.append(f"zaangażowano: {_name(name)} (hp {after_engaged[name]})")
        for name, hp in before_engaged.items():
            if name not in after_engaged:
                changes.append(f"wróg pokonany: {_name(name)}")
            elif after_engaged[name] != hp:
                changes.append(f"{_name(name)} hp: {hp} ->{after_engaged[name]}")

        if after[_SnapshotKey.HAND_SIZE] != before[_SnapshotKey.HAND_SIZE]:
            changes.append(f"ręka: {before[_SnapshotKey.HAND_SIZE]} ->{after[_SnapshotKey.HAND_SIZE]} kart")

        if changes:
            for c in changes:
                Logger.log(f"    -> {c}")
        else:
            Logger.log(f"    -> (brak zmian)")

    # ── Formatters ────────────────────────────────────────────────

    def _fmt_quest(self) -> str:
        if not self.table.quest_deck:
            return "wszystkie ukończone!"
        q = self.table.quest_deck[0]
        loc = self.table.active_travel_location
        loc_str = f"  |  lokacja: {_name(loc)} ({loc.progress}/{loc.required_progress})" if loc else ""
        return f"{_name(q)} ({q.progress}/{q.required_progress}){loc_str}"

    def _fmt_heroes(self) -> str:
        if not self.table.player_heroes:
            return "wszyscy martwi"
        return "  ".join(
            f"{_name(h)} hp={h.hit_points}/{h.max_hit_points} res={h.resource_pool}"
            for h in self.table.player_heroes
        )

    def _fmt_board(self) -> str:
        if not self.table.player_board:
            return "pusta"
        return "  ".join(f"{_name(a)} hp={a.hit_points}" for a in self.table.player_board)

    def _fmt_staging(self) -> str:
        if not self.table.encounter_staging:
            return "pusta"
        return "  ".join(_name(c) for c in self.table.encounter_staging)

    def _fmt_engaged(self) -> str:
        if not self.table.encounter_engagement:
            return "brak"
        return "  ".join(f"{_name(e)} hp={e.hit_points}" for e in self.table.encounter_engagement)
