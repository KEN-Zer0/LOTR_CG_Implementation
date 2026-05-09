from src.cards.creatures.player_creature import PlayerCreature


class Hero(PlayerCreature):
    def __init__(self, name, attack, defense, hitMaxPoints, hitPoints, willpower, sphere, threat):
        super(Hero, self).__init__(name, attack, defense, hitMaxPoints, hitPoints, willpower, sphere)
        self._threat = threat
        self._resourcePool = 0

    @property
    def threat(self):
        return self._threat

    @property
    def resourcePool(self):
        return self._resourcePool

    def changeResourcePool(self, deltaResourcePool):
        self._changeResourcePool += deltaResourcePool

    def addResourceToken(self):
        self._resourcePool += 1

    def copy(self):
        newHero = Hero(
            self.name,
            self.attack,
            self.defense,
            self.hitMaxPoints,
            self.hitPoints,
            self.willpower,
            self.sphere,
            self.threat
        )

        newHero._resourcePool = self.resourcePool
        return newHero
