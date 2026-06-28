"""Human-controlled agent — prompts the player for every decision via stdin."""
from __future__ import annotations

from typing import TYPE_CHECKING

from agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from src.table import Table
    from src.cards import Hero, Ally, Enemy, Location


def _n(card_name: object) -> str:
    return card_name.name if hasattr(card_name, 'name') else str(card_name)


# ── Aligned column formatters ──────────────────────────────────────────────────

def _col_chars(chars: list) -> list[str]:
    """Format heroes/allies with name and sphere columns aligned."""
    name_w   = max(len(_n(c.name))               for c in chars)
    sphere_w = max(len(_n(c.sphere_of_influence)) for c in chars)
    rows = []
    for c in chars:
        name   = _n(c.name).ljust(name_w)
        sphere = f"[{_n(c.sphere_of_influence)}]".ljust(sphere_w + 2)
        hp     = f"{c.hit_points}/{c.max_hit_points}"
        rows.append(f"{name} {sphere}  wp={c.willpower}  atk={c.attack}  def={c.defense}  hp={hp}")
    return rows


def _col_enemies(enemies: list) -> list[str]:
    """Format enemies with name column aligned."""
    name_w = max(len(_n(e.name)) for e in enemies)
    rows = []
    for e in enemies:
        name = _n(e.name).ljust(name_w)
        hp   = f"{e.hit_points}/{e.max_hit_points}"
        rows.append(f"{name}  atk={e.attack}  def={e.defense}  hp={hp}  engagement={e.engagement}  threat={e.threat}")
    return rows


def _col_staging(cards: list) -> list[str]:
    """Format a mixed enemy/location staging list with name column aligned."""
    name_w = max(len(_n(c.name)) for c in cards)
    rows = []
    for c in cards:
        name = _n(c.name).ljust(name_w)
        if hasattr(c, 'engagement'):
            hp = f"{c.hit_points}/{c.max_hit_points}"
            rows.append(f"{name}  atk={c.attack}  def={c.defense}  hp={hp}  engagement={c.engagement}  threat={c.threat}")
        else:
            rows.append(f"{name}  threat={c.threat}  progress={c.progress}/{c.required_progress}  [location]")
    return rows


# ── Input helpers ──────────────────────────────────────────────────────────────

def _pick_one(prompt: str, max_idx: int) -> int | None:
    """Return 0-based index of chosen item, or None if player enters 0 / empty."""
    while True:
        raw = input(prompt).strip()
        if raw in ("0", ""):
            return None
        try:
            i = int(raw)
            if 1 <= i <= max_idx:
                return i - 1
            print(f"  Enter a number between 1 and {max_idx}, or 0 to skip.")
        except ValueError:
            print("  Invalid input — enter a number.")


def _pick_many(prompt: str, max_idx: int) -> list[int]:
    """Return list of unique 0-based indices; empty list if player leaves blank."""
    while True:
        raw = input(prompt).strip()
        if not raw:
            return []
        try:
            indices = [int(x.strip()) for x in raw.split(",") if x.strip()]
            if not all(1 <= i <= max_idx for i in indices):
                print(f"  Enter numbers between 1 and {max_idx}, or leave blank to skip.")
                continue
            seen: set[int] = set()
            unique = [i for i in indices if not (i in seen or seen.add(i))]  # type: ignore[func-returns-value]
            if len(unique) != len(indices):
                print("  Duplicates removed.")
            return [i - 1 for i in unique]
        except ValueError:
            print("  Invalid input — enter comma-separated numbers.")


class HumanAgent(BaseAgent):
    """Interactive agent — prompts the player for every decision via stdin."""

    def choose_questing_characters(
        self, game_state: Table, available: list[Hero | Ally]
    ) -> list[Hero | Ally]:
        staging_threat = sum(c.threat for c in game_state.encounter_staging)
        print(f"\n=== Quest Phase  |  staging threat: {staging_threat} ===")
        if not available:
            print("  (no characters available)")
            return []
        for i, row in enumerate(_col_chars(available), 1):
            print(f"  {i:>2}. {row}")
        indices = _pick_many("  Questers (comma-separated, or blank for none): ", len(available))
        chosen = [available[i] for i in indices]
        if chosen:
            names   = ", ".join(_n(c.name) for c in chosen)
            total_wp = sum(c.willpower for c in chosen)
            net      = total_wp - staging_threat
            net_str  = f"+{net}" if net >= 0 else str(net)
            print(f"  -> Committing: {names}")
            print(f"  -> Total wp: {total_wp}  vs staging threat: {staging_threat}  (net {net_str})")
        else:
            print("  -> No questers committed.")
        return chosen

    def choose_card_to_play(
        self, game_state: Table, playable: list[Ally]
    ) -> Ally | None:
        hand = game_state.player_hand if game_state.player_hand else playable
        if not hand:
            return None
        totals: dict[str, int] = {}
        for h in game_state.player_heroes:
            sphere = _n(h.sphere_of_influence)
            totals[sphere] = totals.get(sphere, 0) + h.resource_pool
        resources = "  ".join(f"{sphere}: {total}" for sphere, total in totals.items())
        print(f"\n=== Planning Phase  |  resources: {resources} ===")
        name_w   = max(len(_n(c.name))               for c in hand)
        sphere_w = max(len(_n(c.sphere_of_influence)) for c in hand)
        playable_ids = {id(c) for c in playable}
        numbered: list[Ally] = []
        for c in hand:
            name   = _n(c.name).ljust(name_w)
            sphere = f"[{_n(c.sphere_of_influence)}]".ljust(sphere_w + 2)
            if id(c) in playable_ids:
                n = len(numbered) + 1
                print(f"  {n:>2}. {name} {sphere}  cost={c.cost}  wp={c.willpower}  atk={c.attack}  def={c.defense}")
                numbered.append(c)
            else:
                print(f"   -  {name} {sphere}  cost={c.cost}  wp={c.willpower}  atk={c.attack}  def={c.defense}  (can't afford)")
        if not numbered:
            print("  (no affordable cards — passing)")
            return None
        idx = _pick_one("  Card to play (0 to pass): ", len(numbered))
        if idx is None:
            print("  -> Pass.")
            return None
        card = numbered[idx]
        print(f"  -> Playing: {_n(card.name)} (cost={card.cost})")
        return card

    def choose_location(
        self, game_state: Table, eligible: list[Location]
    ) -> Location | None:
        if not eligible:
            return None
        print("\n=== Travel Phase ===")
        name_w = max(len(_n(loc.name)) for loc in eligible)
        for i, loc in enumerate(eligible, 1):
            name = _n(loc.name).ljust(name_w)
            print(f"  {i:>2}. {name}  threat={loc.threat}  progress={loc.progress}/{loc.required_progress}")
        idx = _pick_one("  Location to travel to (0 to skip): ", len(eligible))
        if idx is None:
            print("  -> Skip travel.")
            return None
        loc = eligible[idx]
        print(f"  -> Traveling to: {_n(loc.name)}")
        return loc

    def choose_optional_engagement(
        self, game_state: Table, available: list[Enemy]
    ) -> list[Enemy]:
        print(f"\n=== Encounter Phase  |  your threat: {game_state.table_threat} ===")
        print("  Staging:")
        if not game_state.encounter_staging:
            print("    (empty)")
        else:
            for row in _col_staging(game_state.encounter_staging):
                print(f"    {row}")
        print("  Engaged:")
        if not game_state.encounter_engagement:
            print("    (none)")
        else:
            for row in _col_enemies(game_state.encounter_engagement):
                print(f"    {row}")
        if not available:
            return []
        print("  Optional engagement:")
        for i, row in enumerate(_col_enemies(available), 1):
            print(f"    {i:>2}. {row}")
        indices = _pick_many("  Enemies to engage (comma-separated, or blank for none): ", len(available))
        chosen = [available[i] for i in indices]
        if chosen:
            names = ", ".join(_n(e.name) for e in chosen)
            print(f"  -> Engaging: {names}")
        else:
            print("  -> No optional engagement.")
        return chosen

    def choose_defender(
        self, game_state: Table, enemy: Enemy, available: list[Hero | Ally]
    ) -> Hero | Ally | None:
        print(f"\n=== Combat: Defend against {_n(enemy.name)}  atk={enemy.attack} ===")
        if not available:
            print("  (no defenders - attack is undefended)")
            return None
        rows = _col_chars(available)
        dmg_w = max(len(str(max(0, enemy.attack - c.defense))) for c in available)
        for i, (c, row) in enumerate(zip(available, rows), 1):
            dmg = max(0, enemy.attack - c.defense)
            print(f"  {i:>2}. {row}  -> dmg: {dmg:{dmg_w}}")
        idx = _pick_one("  Defender (0 for undefended): ", len(available))
        if idx is None:
            print("  -> Undefended.")
            return None
        defender = available[idx]
        print(f"  -> {_n(defender.name)} defends.")
        return defender

    def choose_undefended_target(
        self, game_state: Table, enemy: Enemy
    ) -> Hero:
        print(f"\n=== Combat: Undefended attack by {_n(enemy.name)}  atk={enemy.attack} ===")
        heroes = game_state.player_heroes
        name_w = max(len(_n(h.name)) for h in heroes)
        for i, h in enumerate(heroes, 1):
            name = _n(h.name).ljust(name_w)
            print(f"  {i:>2}. {name}  hp={h.hit_points}/{h.max_hit_points}")
        while True:
            raw = input("  Who takes the hit? ").strip()
            try:
                i = int(raw)
                if 1 <= i <= len(heroes):
                    target = heroes[i - 1]
                    print(f"  -> {_n(target.name)} takes the hit.")
                    return target
            except ValueError:
                pass
            print(f"  Enter a number between 1 and {len(heroes)}.")

    def choose_attackers(
        self, game_state: Table, enemy: Enemy, available: list[Hero | Ally]
    ) -> list[Hero | Ally]:
        print(f"\n=== Combat: Attack {_n(enemy.name)}  def={enemy.defense}  hp={enemy.hit_points} ===")
        if not available:
            return []
        for i, row in enumerate(_col_chars(available), 1):
            print(f"  {i:>2}. {row}")
        indices = _pick_many("  Attackers (comma-separated, or blank to skip): ", len(available))
        chosen = [available[i] for i in indices]
        if chosen:
            names = ", ".join(_n(c.name) for c in chosen)
            print(f"  -> Attacking with: {names}")
        else:
            print("  -> No attack.")
        return chosen

    # ── Combat result notifications ────────────────────────────────────────────

    def on_defense_resolved(self, enemy: Enemy, defender: Hero | Ally, damage: int) -> None:
        if damage == 0:
            print(f"  -> {_n(defender.name)} blocked all damage (def={defender.defense} >= atk={enemy.attack})")
        elif defender.is_dead():
            hp = defender.hit_points
            print(f"  -> {_n(defender.name)} took {damage} damage and DIED  (hp={hp}/{defender.max_hit_points})")
        else:
            hp = defender.hit_points
            print(f"  -> {_n(defender.name)} took {damage} damage  (hp={hp}/{defender.max_hit_points})")

    def on_undefended_resolved(self, enemy: Enemy, hero: Hero, damage: int) -> None:
        if hero.is_dead():
            hp = hero.hit_points
            print(f"  -> {_n(hero.name)} took {damage} undefended damage and DIED  (hp={hp}/{hero.max_hit_points})")
        else:
            hp = hero.hit_points
            print(f"  -> {_n(hero.name)} took {damage} undefended damage  (hp={hp}/{hero.max_hit_points})")

    def on_attack_resolved(self, enemy: Enemy, attackers: list[Hero | Ally], damage: int, killed: bool) -> None:
        total_atk = sum(a.attack for a in attackers)
        if killed:
            print(f"  -> {_n(enemy.name)} DEFEATED! (dealt {damage} damage, total atk={total_atk})")
        elif damage == 0:
            print(f"  -> No damage (total atk={total_atk} <= def={enemy.defense})")
        else:
            hp = enemy.hit_points
            print(f"  -> Dealt {damage} damage to {_n(enemy.name)}  (hp={hp}/{enemy.max_hit_points})")
