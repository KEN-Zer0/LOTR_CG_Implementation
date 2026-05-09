from src.cards.base_card import BaseCard

class Creature(BaseCard):
    def __init__(self, name, attack, defense, hitPoints):
        super(Creature, self).__init__(name)
        self._attack = attack
        self._defense = defense
        self._hitPoints = hitPoints

    @property
    def attack(self):
        return self._attack

    @property
    def defense(self):
        return self._defense

    @property
    def hitPoints(self):
        return self._hitPoints

    def isDead(self):
        return self.hitPoints <= 0

    def changeHitPoints(self, deltaHP):
        self._hitPoints += deltaHP
