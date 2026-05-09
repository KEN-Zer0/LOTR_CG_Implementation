from src.cards.creatures.base_creature import Creature

class Enemy(Creature):
    def __init__(self, name, attack, defense, hitMaxPoints, hitPoints, engagement, threat):
        super(Enemy, self).__init__(name, attack, defense, hitMaxPoints, hitPoints)
        self._engagement = engagement
        self._threat = threat

    @property
    def engagement(self):
        return self._engagement

    @property
    def threat(self):
        return self._threat

    def copy(self):
        return Enemy(
            self.name,
            self.attack,
            self.defense,
            self.hitMaxPoints,
            self.hitPoints,
            self.engagement,
            self.threat
        )
