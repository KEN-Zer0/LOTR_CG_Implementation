from src.cards.creatures.base_creature import Creature


class PlayerCreature(Creature):
    """Creature controlled by the player, with willpower and an exhausted state."""

    def __init__(
            self,
            name,
            attack,
            defense,
            max_hit_points,
            willpower,
            sphere_of_influence
    ):
        """Initialize; creature starts ready (not exhausted)."""
        super().__init__(name, attack, defense, max_hit_points)

        self._willpower = willpower
        self._sphere_of_influence = sphere_of_influence
        self._exhausted = False

    @property
    def willpower(self):
        """Willpower contributed when this creature commits to the quest."""
        return self._willpower

    @property
    def sphere_of_influence(self):
        """Resource sphere this creature belongs to (Spirit, Tactics, Lore, Leadership, Neutral)."""
        return self._sphere_of_influence

    @property
    def exhausted(self):
        """True after the creature has been committed to quest or combat this round."""
        return self._exhausted

    def is_exhausted(self):
        """Return True if the creature is currently exhausted."""
        return self._exhausted

    def exhaust(self):
        """Mark the creature as exhausted (used in quest, defense, or attack)."""
        self._exhausted = True

    def ready(self):
        """Mark the creature as ready (called during the Refresh phase)."""
        self._exhausted = False

    def is_alive(self):
        """Return True if hit_points > 0."""
        return self.hit_points > 0
