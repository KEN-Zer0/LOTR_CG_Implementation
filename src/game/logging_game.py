from collections import Counter

from config.log_constants import (
    ROUND_SEPARATOR, STATS_SEPARATOR, PHASE_FILL,
    NEW_MARKER, BULLET, INDENT,
    PhaseKey, StatKey, SnapshotKey,
)
from agents.base_agent import BaseAgent
from src.game.game import Game
from src.game.log_formatters import (
    _name, _HeroSnap, _AllySnap, _HandSnap,
    _fmt_hero, _fmt_ally, _fmt_hero_diff, _fmt_ally_diff,
    _sphere_totals, _fmt_staging_card_stats, _bullet_line,
)
from src.logging.logger import Logger


class LoggingGame(Game):
    """Subclass of Game that prints a detailed log of every round and phase."""

    def __init__(self, agent: BaseAgent | None = None) -> None:
        super().__init__(agent=agent)
        self._round = 0
        self._stats = {
            StatKey.RESOURCES_GENERATED: 0,
            StatKey.RESOURCES_SPENT:     0,
            StatKey.ALLIES_PLAYED:       0,
            StatKey.ENEMIES_DEFEATED:    0,
            StatKey.DAMAGE_TO_ENEMIES:   0,
            StatKey.DAMAGE_TO_HEROES:    0,
            StatKey.LOCATIONS_FINISHED:  0,
        }

    def run_round(self) -> None:
        self._round += 1

        Logger.log(f"\n{ROUND_SEPARATOR}")
        Logger.log(f"  ROUND {self._round}")
        Logger.log(f"  Threat:  {self.table.table_threat}/50")
        Logger.log(f"  Quest:   {self._fmt_quest()}")

        if not self.table.player_heroes:
            Logger.log(f"  Heroes:  all dead")
        else:
            Logger.log(f"  Heroes:")
            for h in self.table.player_heroes:
                snap = _HeroSnap(h.name, h.hit_points, h.max_hit_points,
                                 h.resource_pool, h.exhausted, h.sphere_of_influence, h.willpower)
                Logger.log(f"    {_fmt_hero(snap)}")

        Logger.log(f"  Board:")
        if not self.table.player_board:
            Logger.log(f"    (empty)")
        else:
            for a in self.table.player_board:
                snap = _AllySnap(a.name, a.hit_points, a.max_hit_points, a.exhausted, a.willpower)
                Logger.log(f"    {_fmt_ally(snap)}")

        Logger.log(f"  Hand:")
        if not self.table.player_hand:
            Logger.log(f"    (empty)")
        else:
            for c in self.table.player_hand:
                Logger.log(f"    {_name(c.name)} (cost {c.cost})")

        staging_threat = sum(c.threat for c in self.table.encounter_staging)
        Logger.log(f"  Staging: (staging threat: {staging_threat})")
        if not self.table.encounter_staging:
            Logger.log(f"    (empty)")
        else:
            for c in self.table.encounter_staging:
                Logger.log(f"    {_name(c.name)} threat={c.threat}")

        Logger.log(f"  Engaged:")
        if not self.table.encounter_engagement:
            Logger.log(f"    (none)")
        else:
            for e in self.table.encounter_engagement:
                Logger.log(f"    {_name(e.name)} hp={e.hit_points}")

        total = len(self.phases)
        for i, phase in enumerate(self.phases, start=1):
            if self.table.check_win_condition() or self.table.check_lose_condition():
                return
            before = self._snapshot()
            phase_name = phase.__class__.__name__
            Logger.log(f"\n  {PHASE_FILL} [{i}/{total}] {phase_name} {PHASE_FILL}")
            phase.execute()
            self._log_diff(before, phase_name)

    # ── Snapshot ───────────────────────────────────────────────

    def _snapshot(self) -> dict:
        return {
            SnapshotKey.THREAT:              self.table.table_threat,
            SnapshotKey.HEROES:              [
                _HeroSnap(h.name, h.hit_points, h.max_hit_points,
                          h.resource_pool, h.exhausted, h.sphere_of_influence, h.willpower)
                for h in self.table.player_heroes
            ],
            SnapshotKey.BOARD:               [
                _AllySnap(a.name, a.hit_points, a.max_hit_points, a.exhausted, a.willpower)
                for a in self.table.player_board
            ],
            SnapshotKey.STAGING:             [c.name for c in self.table.encounter_staging],
            SnapshotKey.ENGAGED:             [(e.name, e.hit_points) for e in self.table.encounter_engagement],
            SnapshotKey.HAND:                [_HandSnap(c.name, c.cost) for c in self.table.player_hand],
            SnapshotKey.QUEST_NAME:          self.table.quest_deck[0].name if self.table.quest_deck else None,
            SnapshotKey.QUEST_PROGRESS:      self.table.quest_deck[0].progress if self.table.quest_deck else None,
            SnapshotKey.QUEST_REQUIRED:      self.table.quest_deck[0].required_progress if self.table.quest_deck else None,
            SnapshotKey.ACTIVE_LOC:          self.table.active_travel_location.name if self.table.active_travel_location else None,
            SnapshotKey.ACTIVE_LOC_PROGRESS: self.table.active_travel_location.progress if self.table.active_travel_location else None,
            SnapshotKey.TOTAL_RESOURCES:     sum(h.resource_pool for h in self.table.player_heroes),
        }

    # ── Diff ───────────────────────────────────────────────────

    def _log_diff(self, before: dict, phase_name: str = "") -> None:
        after = self._snapshot()
        self._update_stats(before, after, phase_name)
        any_change = False

        if phase_name == PhaseKey.PLANNING:
            any_change |= self._diff_planning_resources(before, after)
        if phase_name == PhaseKey.TRAVEL:
            self._log_travel_state()
            any_change = True
        if phase_name == PhaseKey.ENCOUNTER:
            self._log_encounter_state(before, after)
            any_change = True
        if phase_name == PhaseKey.COMBAT:
            self._log_combat_state()
            any_change = True

        any_change |= self._diff_heroes(before, after, phase_name)
        any_change |= self._diff_board(before, after, phase_name)
        any_change |= self._diff_hand(before, after)
        any_change |= self._diff_threat(before, after)
        any_change |= self._diff_quest(before, after)
        any_change |= self._diff_location(before, after)
        if phase_name != PhaseKey.ENCOUNTER:
            any_change |= self._diff_staging(before, after)
            any_change |= self._diff_engaged(before, after)

        if not any_change:
            Logger.log(f"{BULLET}(no changes)")

    def _diff_planning_resources(self, before: dict, after: dict) -> bool:
        before_spheres = _sphere_totals(before[SnapshotKey.HEROES])
        after_spheres  = _sphere_totals(after[SnapshotKey.HEROES])
        if before_spheres == after_spheres:
            return False
        parts = []
        for sphere in sorted(set(before_spheres) | set(after_spheres)):
            b = before_spheres.get(sphere, 0)
            a = after_spheres.get(sphere, 0)
            parts.append(f"{sphere}: {b}->{a}" if b != a else f"{sphere}: {b}")
        Logger.log(f"{BULLET}resources: {'  '.join(parts)}")
        return True

    def _diff_heroes(self, before: dict, after: dict, phase_name: str) -> bool:
        before_hero_map = {s.name: s for s in before[SnapshotKey.HEROES]}
        after_hero_map  = {s.name: s for s in after[SnapshotKey.HEROES]}
        if before_hero_map == after_hero_map or phase_name == PhaseKey.PLANNING:
            return False
        for name in before_hero_map:
            if name not in after_hero_map:
                Logger.log(f"{BULLET}{_name(name)} DIED")
        for snap in after[SnapshotKey.HEROES]:
            prev = before_hero_map.get(snap.name)
            if prev != snap:
                Logger.log(f"{BULLET}{_fmt_hero_diff(prev, snap)}")
        return True

    def _diff_board(self, before: dict, after: dict, phase_name: str) -> bool:
        before_ally_map = {s.name: s for s in before[SnapshotKey.BOARD]}
        after_ally_map  = {s.name: s for s in after[SnapshotKey.BOARD]}
        if before_ally_map == after_ally_map:
            return False
        for name in before_ally_map:
            if name not in after_ally_map:
                Logger.log(f"{BULLET}ally {_name(name)} died")
        if phase_name == PhaseKey.PLANNING:
            Logger.log(f"{BULLET}Board:")
            for snap in after[SnapshotKey.BOARD]:
                new = snap.name not in before_ally_map
                Logger.log(f"{INDENT}{_fmt_ally(snap, new=new)}")
        else:
            for snap in after[SnapshotKey.BOARD]:
                prev = before_ally_map.get(snap.name)
                if prev is None or prev != snap:
                    Logger.log(f"{BULLET}{_fmt_ally_diff(prev, snap)}")
        return True

    def _diff_hand(self, before: dict, after: dict) -> bool:
        before_hand = before[SnapshotKey.HAND]
        after_hand  = after[SnapshotKey.HAND]
        if before_hand == after_hand:
            return False
        before_hand_names = {s.name for s in before_hand}
        Logger.log(f"{BULLET}Hand:")
        if after_hand:
            for s in after_hand:
                marker = NEW_MARKER if s.name not in before_hand_names else ""
                Logger.log(f"{INDENT}{_name(s.name)} (cost {s.cost}){marker}")
        else:
            Logger.log(f"{INDENT}(empty)")
        return True

    def _diff_threat(self, before: dict, after: dict) -> bool:
        if after[SnapshotKey.THREAT] == before[SnapshotKey.THREAT]:
            return False
        Logger.log(f"{BULLET}threat: {before[SnapshotKey.THREAT]} -> {after[SnapshotKey.THREAT]}")
        return True

    def _diff_quest(self, before: dict, after: dict) -> bool:
        if after[SnapshotKey.QUEST_NAME] != before[SnapshotKey.QUEST_NAME]:
            if not before[SnapshotKey.QUEST_NAME]:
                return False
            after_qn = _name(after[SnapshotKey.QUEST_NAME]) if after[SnapshotKey.QUEST_NAME] else "END"
            overflow = after[SnapshotKey.QUEST_PROGRESS] or 0
            overflow_str = f" ({overflow} tokens carry over)" if overflow > 0 else ""
            Logger.log(f"{BULLET}quest completed: {_name(before[SnapshotKey.QUEST_NAME])} -> {after_qn}{overflow_str}")
            return True
        if (after[SnapshotKey.QUEST_PROGRESS] != before[SnapshotKey.QUEST_PROGRESS]
                and after[SnapshotKey.QUEST_PROGRESS] is not None):
            Logger.log(
                f"{BULLET}quest progress:"
                f" {before[SnapshotKey.QUEST_PROGRESS]}/{after[SnapshotKey.QUEST_REQUIRED]}"
                f" -> {after[SnapshotKey.QUEST_PROGRESS]}/{after[SnapshotKey.QUEST_REQUIRED]}"
            )
            return True
        return False

    def _diff_location(self, before: dict, after: dict) -> bool:
        changed = False
        if (before[SnapshotKey.ACTIVE_LOC]
                and before[SnapshotKey.ACTIVE_LOC] == after[SnapshotKey.ACTIVE_LOC]
                and after[SnapshotKey.ACTIVE_LOC_PROGRESS] != before[SnapshotKey.ACTIVE_LOC_PROGRESS]):
            Logger.log(
                f"{BULLET}location {_name(before[SnapshotKey.ACTIVE_LOC])} progress:"
                f" {before[SnapshotKey.ACTIVE_LOC_PROGRESS]} -> {after[SnapshotKey.ACTIVE_LOC_PROGRESS]}"
            )
            changed = True
        if before[SnapshotKey.ACTIVE_LOC] and not after[SnapshotKey.ACTIVE_LOC]:
            Logger.log(f"{BULLET}location cleared: {_name(before[SnapshotKey.ACTIVE_LOC])}")
            changed = True
        if not before[SnapshotKey.ACTIVE_LOC] and after[SnapshotKey.ACTIVE_LOC]:
            Logger.log(f"{BULLET}active location: {_name(after[SnapshotKey.ACTIVE_LOC])}")
            changed = True
        return changed

    def _diff_staging(self, before: dict, after: dict) -> bool:
        before_staging = Counter(before[SnapshotKey.STAGING])
        after_staging  = Counter(after[SnapshotKey.STAGING])
        changed = False

        for name, count in (after_staging - before_staging).items():
            card = next((c for c in self.table.encounter_staging if c.name == name), None)
            stats = _fmt_staging_card_stats(card)
            suffix = f" [{stats}]" if stats else ""
            Logger.log(_bullet_line(f"revealed: {_name(name)}{suffix}{NEW_MARKER}", count))
            changed = True

        for name, count in (before_staging - after_staging).items():
            Logger.log(_bullet_line(f"removed from staging: {_name(name)}", count))
            changed = True

        return changed

    def _diff_engaged(self, before: dict, after: dict) -> bool:
        before_engaged = dict(before[SnapshotKey.ENGAGED])
        after_engaged  = dict(after[SnapshotKey.ENGAGED])
        changed = False

        for name in after_engaged:
            if name not in before_engaged:
                Logger.log(f"{BULLET}engaged: {_name(name)} (hp {after_engaged[name]}){NEW_MARKER}")
                changed = True

        for name, hp in before_engaged.items():
            if name not in after_engaged:
                Logger.log(f"{BULLET}enemy defeated: {_name(name)}")
                changed = True
            elif after_engaged[name] != hp:
                Logger.log(f"{BULLET}{_name(name)} hp: {hp} -> {after_engaged[name]}")
                changed = True

        return changed

    # ── Travel / Encounter / Combat state ─────────────────────

    def _log_encounter_state(self, before: dict, after: dict) -> None:
        threat = self.table.table_threat
        before_staging = set(before[SnapshotKey.STAGING])
        before_engaged_names = {name for name, _ in before[SnapshotKey.ENGAGED]}

        new_in_staging = [c for c in self.table.encounter_staging if c.name not in before_staging]
        newly_engaged_from_deck = [
            e for e in self.table.encounter_engagement
            if e.name not in before_engaged_names and e.name not in before_staging
        ]
        newly_engaged_from_staging = [
            e for e in self.table.encounter_engagement
            if e.name not in before_engaged_names and e.name in before_staging
        ]

        for card in new_in_staging:
            if hasattr(card, 'engagement'):
                cmp = "<=" if card.engagement <= threat else ">"
                Logger.log(f"{BULLET}revealed: {_name(card.name)} [enemy, engagement_cost={card.engagement} {cmp} threat={threat} → staging]")
            else:
                Logger.log(f"{BULLET}revealed: {_name(card.name)} [location, threat={card.threat} → staging]")

        for enemy in newly_engaged_from_deck:
            if enemy.engagement <= threat:
                Logger.log(f"{BULLET}revealed: {_name(enemy.name)} [enemy, engagement_cost={enemy.engagement} <= threat={threat} → auto-engaged]")
            else:
                Logger.log(f"{BULLET}revealed: {_name(enemy.name)} [enemy, engagement_cost={enemy.engagement} > threat={threat} → optional-engaged]")

        for enemy in newly_engaged_from_staging:
            if enemy.engagement <= threat:
                Logger.log(f"{BULLET}engaged from staging: {_name(enemy.name)} [forced, engagement_cost={enemy.engagement} <= threat={threat}]")
            else:
                Logger.log(f"{BULLET}engaged from staging: {_name(enemy.name)} [optional, engagement_cost={enemy.engagement} > threat={threat}]")

    def _log_travel_state(self) -> None:
        loc = self.table.active_travel_location
        if loc:
            Logger.log(f"{BULLET}Active location: {_name(loc.name)} ({loc.progress}/{loc.required_progress})")
        else:
            Logger.log(f"{BULLET}Active location: none")

    def _log_combat_state(self) -> None:
        threat = self.table.table_threat

        staging_threat = sum(c.threat for c in self.table.encounter_staging)
        Logger.log(f"{BULLET}Staging: (staging threat: {staging_threat})")
        if not self.table.encounter_staging:
            Logger.log(f"{INDENT}(empty)")
        else:
            for card in self.table.encounter_staging:
                if hasattr(card, "engagement"):
                    cmp = ">=" if card.engagement <= threat else "<"
                    Logger.log(
                        f"{INDENT}{_name(card.name)} [enemy]"
                        f" engagement_cost={card.engagement} vs threat={threat} ({cmp}threshold)"
                    )
                else:
                    Logger.log(f"{INDENT}{_name(card.name)} [location] threat={card.threat}")

        Logger.log(f"{BULLET}Engaged:")
        if not self.table.encounter_engagement:
            Logger.log(f"{INDENT}(none)")
        else:
            for e in self.table.encounter_engagement:
                Logger.log(
                    f"{INDENT}{_name(e.name)}"
                    f" hp={e.hit_points}/{e.max_hit_points}"
                    f" atk={e.attack} def={e.defense}"
                )

    # ── Stats ──────────────────────────────────────────────────

    def _update_stats(self, before: dict, after: dict, phase_name: str) -> None:
        if phase_name == PhaseKey.RESOURCES:
            delta = after[SnapshotKey.TOTAL_RESOURCES] - before[SnapshotKey.TOTAL_RESOURCES]
            if delta > 0:
                self._stats[StatKey.RESOURCES_GENERATED] += delta

        if phase_name == PhaseKey.PLANNING:
            delta = before[SnapshotKey.TOTAL_RESOURCES] - after[SnapshotKey.TOTAL_RESOURCES]
            if delta > 0:
                self._stats[StatKey.RESOURCES_SPENT] += delta

            before_names = Counter(s.name for s in before[SnapshotKey.BOARD])
            after_names  = Counter(s.name for s in after[SnapshotKey.BOARD])
            self._stats[StatKey.ALLIES_PLAYED] += sum((after_names - before_names).values())

        if phase_name == PhaseKey.COMBAT:
            before_engaged = dict(before[SnapshotKey.ENGAGED])
            after_engaged  = dict(after[SnapshotKey.ENGAGED])

            for name, hp in before_engaged.items():
                after_hp = after_engaged.get(name, 0)
                if name not in after_engaged:
                    self._stats[StatKey.ENEMIES_DEFEATED] += 1
                self._stats[StatKey.DAMAGE_TO_ENEMIES] += hp - after_hp

            before_hero_map = {s.name: s for s in before[SnapshotKey.HEROES]}
            after_hero_map  = {s.name: s for s in after[SnapshotKey.HEROES]}

            for name, snap in before_hero_map.items():
                after_snap = after_hero_map.get(name)
                after_hp   = after_snap.hp if after_snap else 0
                if after_hp < snap.hp:
                    self._stats[StatKey.DAMAGE_TO_HEROES] += snap.hp - after_hp

        if before[SnapshotKey.ACTIVE_LOC] and not after[SnapshotKey.ACTIVE_LOC]:
            self._stats[StatKey.LOCATIONS_FINISHED] += 1

    # ── Summary ────────────────────────────────────────────────

    def log_summary(self, is_victory: bool) -> None:
        if is_victory:
            outcome = "VICTORY"
        elif self.table.is_threat_too_high():
            outcome = "DEFEAT — Threat reached 50"
        else:
            outcome = "DEFEAT — All heroes dead"

        Logger.log(f"\n{ROUND_SEPARATOR}")
        Logger.log(f"  GAME STATISTICS")
        Logger.log(ROUND_SEPARATOR)
        Logger.log(f"  >>> {outcome} <<<")
        Logger.log(STATS_SEPARATOR)
        Logger.log(f"  Rounds:               {self._round}")
        Logger.log(f"  Heroes alive:         {len(self.table.player_heroes)}")
        Logger.log(f"  Final threat:         {self.table.table_threat}")
        Logger.log(STATS_SEPARATOR)
        Logger.log(f"  Resources generated:  {self._stats[StatKey.RESOURCES_GENERATED]}")
        Logger.log(f"  Resources spent:      {self._stats[StatKey.RESOURCES_SPENT]}")
        Logger.log(f"  Allies played:        {self._stats[StatKey.ALLIES_PLAYED]}")
        Logger.log(f"  Enemies defeated:     {self._stats[StatKey.ENEMIES_DEFEATED]}")
        Logger.log(f"  Locations cleared:    {self._stats[StatKey.LOCATIONS_FINISHED]}")
        Logger.log(f"  Damage dealt:         {self._stats[StatKey.DAMAGE_TO_ENEMIES]}")
        Logger.log(f"  Damage received:      {self._stats[StatKey.DAMAGE_TO_HEROES]}")
        Logger.log(ROUND_SEPARATOR)

    # ── Quest formatter ────────────────────────────────────────

    def _fmt_quest(self) -> str:
        if not self.table.quest_deck:
            return "all completed!"
        q = self.table.quest_deck[0]
        loc = self.table.active_travel_location
        loc_str = f"  |  location: {_name(loc.name)} ({loc.progress}/{loc.required_progress})" if loc else ""
        return f"{_name(q)} ({q.progress}/{q.required_progress}){loc_str}"
