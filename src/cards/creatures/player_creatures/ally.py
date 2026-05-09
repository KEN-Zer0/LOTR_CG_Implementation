from src.cards.creatures.player_creature import PlayerCreature


class Ally(PlayerCreature):
    def __init__(self, name, attack, defense, hitMaxPoints, hitPoints, willpower, sphere, cost):
        super(Ally, self).__init__(name, attack, defense, hitMaxPoints, hitPoints, willpower, sphere)
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
