from __future__ import annotations

from typing import TYPE_CHECKING

from agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from src.table import Table
    from src.cards import Hero, Ally, Enemy, Location


class ExpertAgent(BaseAgent):
    """Heuristic agent driven by hardcoded if/else logic.

    Quest phase  : commit all available characters with willpower > 0.
    Planning     : always play the cheapest affordable card first.
    Travel       : travel to the location with the highest threat to shrink staging.
    Engagement   : never voluntarily engage (let forced engagement handle it).
    Defense      : sacrifice a cheap chump blocker when possible; otherwise use
                   the character with the highest defense rating.
    Undefended   : direct unblocked damage to the hero with the most hit points.
    Attack       : commit the fewest characters needed to kill the enemy;
                   commit everyone if the enemy cannot be killed this round.
    """

    def choose_questing_characters(
        self, game_state: Table, available: list[Hero | Ally]
    ) -> list[Hero | Ally]:
        return [c for c in available if c.willpower > 0]

    def choose_card_to_play(
        self, game_state: Table, playable: list[Ally]
    ) -> Ally | None:
        if not playable:
            return None
        return min(playable, key=lambda card: card.cost)

    def choose_location(
        self, game_state: Table, eligible: list[Location]
    ) -> Location | None:
        return max(eligible, key=lambda loc: loc.threat)

    def choose_optional_engagement(
        self, game_state: Table, available: list[Enemy]
    ) -> list[Enemy]:
        return []

    def choose_defender(
        self, game_state: Table, enemy: Enemy, available: list[Hero | Ally]
    ) -> Hero | Ally | None:
        if not available:
            return None

        # Use an ally as a chump blocker when the attack would kill it anyway —
        # this sacrifices a weak ally instead of a valuable hero or better ally.
        allies = [c for c in available if hasattr(c, "cost")]
        if allies:
            doomed = [a for a in allies if a.hit_points <= enemy.attack - a.defense]
            if doomed:
                return min(doomed, key=lambda a: a.hit_points)

        return max(available, key=lambda c: c.defense)

    def choose_undefended_target(
        self, game_state: Table, enemy: Enemy
    ) -> Hero:
        return max(game_state.player_heroes, key=lambda h: h.hit_points)

    def choose_attackers(
        self, game_state: Table, enemy: Enemy, available: list[Hero | Ally]
    ) -> list[Hero | Ally]:
        if not available:
            return []

        # Commit fewest attackers (sorted by attack desc) sufficient to kill;
        # fall back to all available if the enemy cannot be killed this round.
        by_attack = sorted(available, key=lambda c: c.attack, reverse=True)
        chosen, total = [], 0
        for char in by_attack:
            chosen.append(char)
            total += char.attack
            if total - enemy.defense >= enemy.hit_points:
                return chosen

        return list(available)
