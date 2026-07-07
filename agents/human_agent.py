"""Human-controlled agent — prompts the player for every decision via stdin."""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from src.table import Table
    from src.cards import Hero, Ally, Enemy, Location

# Enable ANSI escape sequences on Windows 10 consoles.
os.system("")

# ── ANSI color helpers ─────────────────────────────────────────────────────────

R   = "\033[0m"       # reset
B   = "\033[1m"       # bold
DIM = "\033[2m"

CYAN    = "\033[96m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
RED     = "\033[91m"
GREEN   = "\033[92m"
WHITE   = "\033[97m"


def _c(color: str, text: str) -> str:
    return f"{color}{text}{R}"


def _header(color: str, text: str) -> str:
    return f"\n{B}{color}=== {text} ==={R}"


# ── Card name helper ───────────────────────────────────────────────────────────

def _n(card_name: object) -> str:
    return card_name.name if hasattr(card_name, "name") else str(card_name)


# ── Aligned column formatters ──────────────────────────────────────────────────

def _col_chars(chars: list) -> list[str]:
    """Format heroes/allies with name and sphere columns aligned."""
    name_w   = max(len(_n(c.name))               for c in chars)
    sphere_w = max(len(_n(c.sphere_of_influence)) for c in chars)
    rows = []
    for c in chars:
        name   = _n(c.name).ljust(name_w)
        sphere = f"[{_n(c.sphere_of_influence)}]".ljust(sphere_w + 2)
        hp     = _c(RED, f"{c.hit_points}/{c.max_hit_points}")
        rows.append(
            f"{name} {sphere}"
            f"  wp={_c(CYAN, str(c.willpower))}"
            f"  atk={c.attack}"
            f"  def={_c(BLUE, str(c.defense))}"
            f"  hp={hp}"
        )
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
        if hasattr(c, "engagement"):
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


# ── One-time intro ─────────────────────────────────────────────────────────────

def _print_intro() -> None:
    print(f"\n{B}{CYAN}{'='*52}{R}")
    print(f"{B}{CYAN}  LOTR Card Game  |  Passage Through Mirkwood{R}")
    print(f"{B}{CYAN}{'='*52}{R}")
    print(f"\n  {B}7 faz na runde:{R}")
    print(f"  {YELLOW}1. Resources {R} — herosi dostaja zasoby  {DIM}(auto){R}")
    print(f"  {YELLOW}2. Planning  {R} — zagraj Ally z reki")
    print(f"  {CYAN}3. Quest     {R} — wybierz questujacych  {DIM}(willpower vs staging threat){R}")
    print(f"  {BLUE}4. Travel    {R} — wejdz na lokacje ze stagingu")
    print(f"  {MAGENTA}5. Encounter {R} — wrogowie angażują sie  {DIM}(engagement <= twoj threat){R}")
    print(f"  {RED}6. Combat    {R} — obron sie, atakuj wrogów")
    print(f"  {WHITE}7. Refresh   {R} — odswiez karty, zagrożenie +1  {DIM}(auto){R}")
    print(f"\n  {B}Cel:{R} ukoncz 3 karty questow zanim zagrożenie = {RED}50{R} lub wszyscy herosi zgina.")
    print()


class HumanAgent(BaseAgent):
    """Interactive agent — prompts the player for every decision via stdin."""

    def __init__(self) -> None:
        _print_intro()

    # ── Quest ──────────────────────────────────────────────────────────────────

    def choose_questing_characters(
        self, game_state: Table, available: list[Hero | Ally]
    ) -> list[Hero | Ally]:
        staging_threat = sum(c.threat for c in game_state.encounter_staging)
        print(_header(CYAN, f"Quest Phase  |  staging threat: {staging_threat}"))
        if not available:
            print("  (no characters available)")
            return []
        for i, row in enumerate(_col_chars(available), 1):
            print(f"  {i:>2}. {row}")
        indices = _pick_many("  Questers (comma-separated, or blank for none): ", len(available))
        chosen = [available[i] for i in indices]
        if chosen:
            names    = ", ".join(_n(c.name) for c in chosen)
            total_wp = sum(c.willpower for c in chosen)
            net      = total_wp - staging_threat
            net_str  = _c(GREEN, f"+{net}") if net >= 0 else _c(RED, str(net))
            print(f"  -> Committing: {names}")
            print(f"  -> Total wp: {total_wp}  vs staging threat: {staging_threat}  (net {net_str})")
        else:
            print(f"  -> {_c(YELLOW, 'No questers committed.')}")
        return chosen

    # ── Planning ───────────────────────────────────────────────────────────────

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
        print(_header(YELLOW, f"Planning Phase  |  resources: {resources}"))
        name_w   = max(len(_n(c.name))               for c in hand)
        sphere_w = max(len(_n(c.sphere_of_influence)) for c in hand)
        playable_ids = {id(c) for c in playable}
        sorted_hand  = sorted(hand, key=lambda c: (0 if id(c) in playable_ids else 1, _n(c.name)))
        numbered: list[Ally] = []
        for c in sorted_hand:
            name   = _n(c.name).ljust(name_w)
            sphere = f"[{_n(c.sphere_of_influence)}]".ljust(sphere_w + 2)
            stats  = (
                f"cost={_c(YELLOW, str(c.cost))}"
                f"  wp={_c(CYAN, str(c.willpower))}"
                f"  atk={c.attack}"
                f"  def={_c(BLUE, str(c.defense))}"
            )
            if id(c) in playable_ids:
                n = len(numbered) + 1
                print(f"  {n:>2}. {_c(GREEN, name)} {sphere}  {stats}")
                numbered.append(c)
            else:
                cant = "(can't afford)"
                print(f"  {DIM} -  {name} {sphere}  {stats}  {_c(RED, cant)}{R}")
        if not numbered:
            print(f"  {_c(DIM, '(no affordable cards — passing)')}")
            return None
        idx = _pick_one("  Card to play (0 to pass): ", len(numbered))
        if idx is None:
            print("  -> Pass.")
            return None
        card = numbered[idx]
        print(f"  -> Playing: {_c(GREEN, _n(card.name))} (cost={card.cost})")
        return card

    # ── Travel ─────────────────────────────────────────────────────────────────

    def choose_location(
        self, game_state: Table, eligible: list[Location]
    ) -> Location | None:
        if not eligible:
            return None
        print(_header(BLUE, "Travel Phase"))
        name_w = max(len(_n(loc.name)) for loc in eligible)
        for i, loc in enumerate(eligible, 1):
            name = _n(loc.name).ljust(name_w)
            print(f"  {i:>2}. {name}  threat={loc.threat}  progress={loc.progress}/{loc.required_progress}")
        idx = _pick_one("  Location to travel to (0 to skip): ", len(eligible))
        if idx is None:
            print("  -> Skip travel.")
            return None
        loc = eligible[idx]
        print(f"  -> Traveling to: {_c(BLUE, _n(loc.name))}")
        return loc

    # ── Encounter ──────────────────────────────────────────────────────────────

    def choose_optional_engagement(
        self, game_state: Table, available: list[Enemy]
    ) -> list[Enemy]:
        threat = game_state.table_threat
        threat_str = _c(RED, str(threat)) if threat >= 40 else _c(YELLOW, str(threat)) if threat >= 30 else str(threat)
        print(_header(MAGENTA, f"Encounter Phase  |  your threat: {threat_str}"))
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
                print(f"    {_c(RED, row)}")
        if not available:
            return []
        auto = [e for e in available if e.engagement <= threat]
        if auto:
            print(f"  {_c(MAGENTA, 'Will auto-engage:')}")
            for row in _col_enemies(auto):
                print(f"    {_c(MAGENTA, row)}")
        print("  Optional engagement:")
        numbered: list[Enemy] = []
        for e in available:
            marker = _c(MAGENTA, " [auto]") if e.engagement <= threat else ""
            n = len(numbered) + 1
            row = _col_enemies([e])[0]
            print(f"    {n:>2}. {row}{marker}")
            numbered.append(e)
        indices = _pick_many("  Enemies to engage (comma-separated, or blank for none): ", len(available))
        chosen = [available[i] for i in indices]
        if chosen:
            names = ", ".join(_n(e.name) for e in chosen)
            print(f"  -> Engaging: {_c(MAGENTA, names)}")
        else:
            print("  -> No optional engagement.")
        return chosen

    # ── Combat: defend ─────────────────────────────────────────────────────────

    def choose_defender(
        self, game_state: Table, enemy: Enemy, available: list[Hero | Ally]
    ) -> Hero | Ally | None:
        print(_header(RED, f"Combat: Defend against {_n(enemy.name)}  atk={enemy.attack}"))
        if not available:
            print(f"  {_c(RED, '(no defenders — attack is undefended)')}")
            return None
        rows = _col_chars(available)
        dmg_w = max(len(str(max(0, enemy.attack - c.defense))) for c in available)
        for i, (c, row) in enumerate(zip(available, rows), 1):
            dmg = max(0, enemy.attack - c.defense)
            dmg_col = _c(RED, str(dmg)) if dmg >= c.hit_points else _c(YELLOW, str(dmg)) if dmg > 0 else _c(GREEN, "0")
            print(f"  {i:>2}. {row}  -> dmg: {dmg_col}")
        idx = _pick_one("  Defender (0 for undefended): ", len(available))
        if idx is None:
            print(f"  -> {_c(YELLOW, 'Undefended.')}")
            return None
        defender = available[idx]
        print(f"  -> {_n(defender.name)} defends.")
        return defender

    # ── Combat: undefended target ──────────────────────────────────────────────

    def choose_undefended_target(
        self, game_state: Table, enemy: Enemy
    ) -> Hero:
        print(_header(RED, f"Combat: Undefended attack by {_n(enemy.name)}  atk={enemy.attack}"))
        heroes = game_state.player_heroes
        name_w = max(len(_n(h.name)) for h in heroes)
        for i, h in enumerate(heroes, 1):
            name    = _n(h.name).ljust(name_w)
            hp_col  = _c(RED, f"{h.hit_points}/{h.max_hit_points}") if h.hit_points <= enemy.attack else f"{h.hit_points}/{h.max_hit_points}"
            print(f"  {i:>2}. {name}  hp={hp_col}")
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

    # ── Combat: attack ─────────────────────────────────────────────────────────

    def choose_attackers(
        self, game_state: Table, enemy: Enemy, available: list[Hero | Ally]
    ) -> list[Hero | Ally]:
        print(_header(RED, f"Combat: Attack {_n(enemy.name)}  def={enemy.defense}  hp={enemy.hit_points}"))
        if not available:
            print(f"  {_c(DIM, '(no available attackers)')}")
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
            print(f"  -> {_c(GREEN, f'{_n(defender.name)} blocked all damage')}  (def={defender.defense} >= atk={enemy.attack})")
        elif defender.is_dead():
            print(f"  -> {_c(RED, f'{_n(defender.name)} took {damage} damage and DIED')}  (hp={defender.hit_points}/{defender.max_hit_points})")
        else:
            print(f"  -> {_c(YELLOW, f'{_n(defender.name)} took {damage} damage')}  (hp={defender.hit_points}/{defender.max_hit_points})")

    def on_undefended_resolved(self, enemy: Enemy, hero: Hero, damage: int) -> None:
        if hero.is_dead():
            print(f"  -> {_c(RED, B + f'{_n(hero.name)} took {damage} undefended damage and DIED' + R)}  (hp={hero.hit_points}/{hero.max_hit_points})")
        else:
            print(f"  -> {_c(YELLOW, f'{_n(hero.name)} took {damage} undefended damage')}  (hp={hero.hit_points}/{hero.max_hit_points})")

    def on_no_heroes_for_undefended(self, enemy: Enemy) -> None:
        msg = f"(all heroes dead — {_n(enemy.name)}'s attack skipped)"
        print(f"  {_c(DIM, msg)}")

    def on_attack_resolved(self, enemy: Enemy, attackers: list[Hero | Ally], damage: int, killed: bool) -> None:
        total_atk = sum(a.attack for a in attackers)
        if killed:
            print(f"  -> {_c(GREEN, B + f'{_n(enemy.name)} DEFEATED!' + R)}  (dealt {damage}, total atk={total_atk})")
        elif damage == 0:
            print(f"  -> {_c(DIM, f'No damage  (total atk={total_atk} <= def={enemy.defense})')}")
        else:
            print(f"  -> {_c(YELLOW, f'Dealt {damage} damage to {_n(enemy.name)}')}  (hp={enemy.hit_points}/{enemy.max_hit_points})")
