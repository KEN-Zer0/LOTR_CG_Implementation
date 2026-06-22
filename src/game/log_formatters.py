from collections import defaultdict
from typing import NamedTuple

from config.log_constants import NEW_MARKER, BULLET, CardState


def _name(x) -> str:
    """Convert a card object, Enum value, or fallback string to a display name."""
    if isinstance(x, str):
        return x
    n = x.name
    if isinstance(n, str):
        return n
    return n.name if hasattr(n, "name") else str(n)


def _state(exhausted: bool) -> str:
    return CardState.EXHAUSTED if exhausted else CardState.READY


def _bullet_line(label: str, count: int = 1) -> str:
    return f"{BULLET}{label} x{count}" if count > 1 else f"{BULLET}{label}"


# ── Snapshot types ─────────────────────────────────────────────

class _HeroSnap(NamedTuple):
    name:      object
    hp:        int
    max_hp:    int
    res:       int
    exhausted: bool
    sphere:    object
    willpower: int


class _AllySnap(NamedTuple):
    name:      object
    hp:        int
    max_hp:    int
    exhausted: bool
    willpower: int


class _HandSnap(NamedTuple):
    name: object
    cost: int


# ── Formatters ─────────────────────────────────────────────────

def _fmt_hero(snap: _HeroSnap) -> str:
    return (
        f"{_name(snap.name)} [{_name(snap.sphere)}]"
        f" hp={snap.hp}/{snap.max_hp}"
        f" wp={snap.willpower}"
        f" res={snap.res}"
        f" {_state(snap.exhausted)}"
    )


def _fmt_ally(snap: _AllySnap, new: bool = False) -> str:
    suffix = NEW_MARKER if new else ""
    return (
        f"{_name(snap.name)}"
        f" hp={snap.hp}/{snap.max_hp}"
        f" wp={snap.willpower}"
        f" {_state(snap.exhausted)}{suffix}"
    )


def _fmt_hero_diff(prev: _HeroSnap | None, curr: _HeroSnap) -> str:
    if prev is None:
        return _fmt_hero(curr)

    changes = []
    if prev.hp != curr.hp:
        changes.append(f"hp {prev.hp}->{curr.hp}")
    if prev.res != curr.res:
        changes.append(f"res {prev.res}->{curr.res}")
    if prev.exhausted != curr.exhausted:
        changes.append(f"{_state(prev.exhausted)}->{_state(curr.exhausted)}")

    if not changes:
        return _fmt_hero(curr)
    return f"{_name(curr.name)}: " + "  ".join(changes)


def _fmt_ally_diff(prev: _AllySnap | None, curr: _AllySnap) -> str:
    if prev is None:
        return _fmt_ally(curr, new=True)

    changes = []
    if prev.hp != curr.hp:
        changes.append(f"hp {prev.hp}->{curr.hp}")
    if prev.exhausted != curr.exhausted:
        changes.append(f"{_state(prev.exhausted)}->{_state(curr.exhausted)}")

    if not changes:
        return _fmt_ally(curr)
    return f"{_name(curr.name)}: " + "  ".join(changes)


def _sphere_totals(heroes: list[_HeroSnap]) -> dict[str, int]:
    result: dict[str, int] = defaultdict(int)
    for h in heroes:
        result[_name(h.sphere)] += h.res
    return dict(result)


def _fmt_staging_card_stats(card) -> str:
    if hasattr(card, "engagement"):
        return f"atk={card.attack} def={card.defense} hp={card.hit_points} threat={card.threat} engagement_cost={card.engagement}"
    if hasattr(card, "required_progress"):
        return f"threat={card.threat} quest_progress={card.progress}/{card.required_progress}"
    # TODO: treachery card logging goes here
    return ""
