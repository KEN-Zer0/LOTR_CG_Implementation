from src.cards.creatures.player_creatures import PlayerCreature


class Ally(PlayerCreature):
    """Player card that can be recruited from hand during the Planning phase."""

    def __init__(
            self,
            name,
            attack,
            defense,
            max_hit_points,
            willpower,
            sphere_of_influence,
            cost
    ):
        """Initialize ally with a resource cost required to play from hand."""
        super().__init__(name, attack, defense, max_hit_points, willpower, sphere_of_influence)

        self._cost = cost

    @property
    def cost(self):
        """Resource tokens required to play this ally from hand."""
        return self._cost

    def copy(self):
        """Return a new Ally with identical stats and the same current hit_points."""
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
