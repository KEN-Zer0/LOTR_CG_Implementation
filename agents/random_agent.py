from __future__ import annotations

import random
from typing import TYPE_CHECKING

from agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from src.table import Table
    from src.cards import Hero, Ally, Enemy, Location


class RandomAgent(BaseAgent):
    """Makes all decisions uniformly at random using the stdlib random module."""

    def choose_questing_characters(
        self, game_state: Table, available: list[Hero | Ally]
    ) -> list[Hero | Ally]:
        k = random.randint(0, len(available))
        return random.sample(available, k)

    def choose_card_to_play(
        self, game_state: Table, playable: list[Ally]
    ) -> Ally | None:
        # Include None so there is a chance to pass and end the phase early.
        if not playable:
            return None
        return random.choice(playable + [None])

    def choose_location(
        self, game_state: Table, eligible: list[Location]
    ) -> Location | None:
        return random.choice(eligible + [None])

    def choose_optional_engagement(
        self, game_state: Table, available: list[Enemy]
    ) -> list[Enemy]:
        k = random.randint(0, len(available))
        return random.sample(available, k)

    def choose_defender(
        self, game_state: Table, enemy: Enemy, available: list[Hero | Ally]
    ) -> Hero | Ally | None:
        if not available:
            return None
        return random.choice(available + [None])

    def choose_undefended_target(
        self, game_state: Table, enemy: Enemy
    ) -> Hero:
        return random.choice(game_state.player_heroes)

    def choose_attackers(
        self, game_state: Table, enemy: Enemy, available: list[Hero | Ally]
    ) -> list[Hero | Ally]:
        if not available:
            return []
        k = random.randint(0, len(available))
        return random.sample(available, k)
