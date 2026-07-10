from enum import Enum

from src.cards.base_card import BaseCard


class Creature(BaseCard):
    """Base class for all creature cards — holds combat stats and hit points."""

    def __init__(
            self,
            name: Enum,
            attack: int,
            defense: int,
            max_hit_points: int
    ) -> None:
        """Initialize combat stats; hit_points starts equal to max_hit_points.

        Args:
            name (Enum): Enum identifier for this creature.
            attack (int): Damage dealt per combat attack.
            defense (int): Damage absorbed before applying net damage to hit_points.
            max_hit_points (int): Maximum and starting hit points.
        """
        super().__init__(name)

        self._attack = attack
        self._defense = defense
        self._max_hit_points = max_hit_points
        self._hit_points = max_hit_points

    @property
    def attack(self) -> int:
        """int: Damage dealt per combat attack."""
        return self._attack

    @property
    def defense(self) -> int:
        """int: Damage absorbed before applying net damage to hit_points."""
        return self._defense

    @property
    def max_hit_points(self) -> int:
        """int: Maximum hit points; hit_points is clamped to this ceiling."""
        return self._max_hit_points

    @property
    def hit_points(self) -> int:
        """int: Current remaining hit points; floored at 0."""
        return self._hit_points

    def is_dead(self) -> bool:
        """Check whether the creature has been defeated.

        Returns:
            bool: True when hit_points have reached 0.
        """
        return self._hit_points <= 0

    def take_damage(self, damage: int) -> None:
        """Reduce hit_points by damage (delegates to change_hp).

        Args:
            damage (int): Amount of damage to apply.
        """
        self.change_hp(-damage)

    def change_hp(self, delta_hp: int) -> None:
        """Add delta_hp to hit_points, clamped to [0, max_hit_points].

        Args:
            delta_hp (int): Amount to add (use a negative value to subtract).
        """
        self._hit_points += delta_hp

        if self._hit_points > self._max_hit_points:
            self._hit_points = self._max_hit_points

        if self._hit_points < 0:
            self._hit_points = 0
