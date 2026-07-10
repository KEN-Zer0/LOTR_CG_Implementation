from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config.limited.cards_list import Sphere

from src.cards.creatures.player_creatures import PlayerCreature


class Hero(PlayerCreature):
    """Player-controlled hero with a fixed threat cost and a resource pool."""

    def __init__(
            self,
            name: Enum,
            attack: int,
            defense: int,
            max_hit_points: int,
            willpower: int,
            sphere_of_influence: Sphere,
            threat: int
    ) -> None:
        """Initialize hero; resource_pool starts at 0.

        Args:
            name (Enum): Enum identifier for this hero.
            attack (int): Damage dealt per combat attack.
            defense (int): Damage absorbed before applying net damage to hit_points.
            max_hit_points (int): Maximum and starting hit points.
            willpower (int): Willpower contributed when committed to the quest.
            sphere_of_influence (Sphere): Resource sphere this hero belongs to.
            threat (int): Starting-threat contribution added to the player's total at game start.
        """
        super().__init__(name, attack, defense, max_hit_points, willpower, sphere_of_influence)

        self._threat = threat
        self._resource_pool = 0

    @property
    def threat(self) -> int:
        """int: Starting-threat contribution added to the player's threat total at game start."""
        return self._threat

    @property
    def resource_pool(self) -> int:
        """int: Current number of resource tokens available for paying card costs."""
        return self._resource_pool

    def change_resource_pool(self, delta: int) -> None:
        """Add delta to resource_pool, floored at 0.

        Args:
            delta (int): Amount to add (use a negative value to spend resources).
        """
        self._resource_pool += delta

        if self._resource_pool < 0:
            self._resource_pool = 0

    def add_resource_token(self) -> None:
        """Increase resource_pool by 1 (shortcut for change_resource_pool(1))."""
        self._resource_pool += 1

    def copy(self):
        """Create a copy of this hero with identical stats and the same current resource_pool.

        Returns:
            Hero: A new Hero instance with copied stats and resource pool.
        """
        new_hero = Hero(
            self.name,
            self.attack,
            self.defense,
            self.max_hit_points,
            self.willpower,
            self.sphere_of_influence,
            self.threat
        )

        new_hero._resource_pool = self._resource_pool
        return new_hero
