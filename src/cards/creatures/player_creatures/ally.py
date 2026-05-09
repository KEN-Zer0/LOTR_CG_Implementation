from src.cards.creatures.player_creatures import PlayerCreature


class Ally(PlayerCreature):
    def __init__(
            self,
            name,
            attack,
            defense,
            hit_max_points,
            hit_points,
            willpower,
            sphere,
            cost
    ):
        super().__init__(
            name,
            attack,
            defense,
            hit_max_points,
            hit_points,
            willpower,
            sphere
        )

        self._cost = cost

    @property
    def cost(self):
        return self._cost

    def copy(self):
        newAlly = Ally(
            self.name,
            self.attack,
            self.defense,
            self.hitMaxPoints,
            self.hitPoints,
            self.willpower,
            self.sphere,
            self.cost
        )

        return newAlly
