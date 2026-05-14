from src.cards.creatures.player_creatures import PlayerCreature


class Ally(PlayerCreature):
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
        super().__init__(
            name,
            attack,
            defense,
            max_hit_points,
            willpower,
            sphere_of_influence
        )

        self._cost = cost

    @property
    def cost(self):
        return self._cost

    def copy(self):
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