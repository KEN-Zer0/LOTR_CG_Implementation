from enum import Enum

from src.cards.creatures.base_creature import Creature


class Enemy(Creature):
    """Encounter-deck creature with a staging threat value and an engagement cost."""

    def __init__(
            self,
            name: Enum,
            attack: int,
            defense: int,
            max_hit_points: int,
            engagement: int,
            threat: int
    ) -> None:
        """Initialize the enemy.

        Args:
            name (Enum): Enum identifier for this enemy.
            attack (int): Damage dealt per combat attack.
            defense (int): Damage absorbed before applying net damage to hit_points.
            max_hit_points (int): Maximum and starting hit points.
            engagement (int): Table-threat threshold at or above which this enemy auto-engages.
            threat (int): Staging-area threat contributed each round while unengaged.
        """
        super().__init__(name, attack, defense, max_hit_points)

        self._engagement = engagement
        self._threat = threat

    @property
    def engagement(self) -> int:
        """int: Table-threat value at or above which this enemy automatically engages the player."""
        return self._engagement

    @property
    def threat(self) -> int:
        """int: Staging-area threat contribution while the enemy remains unengaged."""
        return self._threat

    def copy(self):
        """Create a fresh copy of this enemy with identical stats and full hit points.

        Returns:
            Enemy: A new Enemy instance with the same stats.
        """
        return Enemy(
            self.name,
            self.attack,
            self.defense,
            self.max_hit_points,
            self.engagement,
            self.threat
        )
