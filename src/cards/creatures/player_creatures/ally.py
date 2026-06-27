from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config.limited.cards_list import Sphere

from src.cards.creatures.player_creatures import PlayerCreature


class Ally(PlayerCreature):
    """Player card that can be recruited from hand during the Planning phase."""

    def __init__(
            self,
            name: Enum,
            attack: int,
            defense: int,
            max_hit_points: int,
            willpower: int,
            sphere_of_influence: Sphere,
            cost: int
    ) -> None:
        """Initialize ally with a resource cost required to play from hand.

        Args:
            name (Enum): Enum identifier for this ally.
            attack (int): Damage dealt per combat attack.
            defense (int): Damage absorbed before applying net damage to hit_points.
            max_hit_points (int): Maximum and starting hit points.
            willpower (int): Willpower contributed when committed to the quest.
            sphere_of_influence (Sphere): Resource sphere this ally belongs to.
            cost (int): Resource tokens required to play this ally from hand.
        """
        super().__init__(name, attack, defense, max_hit_points, willpower, sphere_of_influence)

        self._cost = cost

    @property
    def cost(self) -> int:
        """int: Resource tokens required to play this ally from hand."""
        return self._cost

    def copy(self):
        """Create a copy of this ally with identical stats and the same current hit_points.

        Returns:
            Ally: A new Ally instance with copied stats and hit points.
        """
        new_ally = Ally(
            self.name,
            self.attack,
            self.defense,
            self.max_hit_points,
            self.willpower,
            self.sphere_of_influence,
            self.cost
        )

        new_ally._hit_points = self.hit_points
        return new_ally
