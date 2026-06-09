from src.cards.creatures.base_creature import Creature


class Enemy(Creature):
    """Encounter-deck creature with a staging threat value and an engagement cost."""

    def __init__(
            self,
            name,
            attack,
            defense,
            max_hit_points,
            engagement,
            threat
    ):
        """
        Initialize enemy.

        Parameters
        ----------
        engagement : int
            Table-threat threshold at or above which this enemy auto-engages.
        threat : int
            Staging-area threat contributed each round while unengaged.
        """
        super().__init__(name, attack, defense, max_hit_points)

        self._engagement = engagement
        self._threat = threat

    @property
    def engagement(self):
        """Table-threat value at or above which this enemy automatically engages the player."""
        return self._engagement

    @property
    def threat(self):
        """Staging-area threat contribution while the enemy remains unengaged."""
        return self._threat

    def copy(self):
        """Return a fresh Enemy with identical stats and full hit points."""
        return Enemy(
            self.name,
            self.attack,
            self.defense,
            self.max_hit_points,
            self.engagement,
            self.threat
        )
