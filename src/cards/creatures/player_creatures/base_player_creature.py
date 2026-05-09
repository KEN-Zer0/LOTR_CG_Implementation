from src.cards.creatures.base_creature import Creature


class PlayerCreature(Creature):
    def __init__(self, name, attack, defense, hitMaxPoints, hitPoints, willpower, sphere):
        super(PlayerCreature, self).__init__(name, attack, defense, hitMaxPoints, hitPoints)
        self._willpower = willpower
        self._sphere = sphere
        self._tapped = False

    @property
    def willpower(self):
        return self._willpower

    @property
    def sphere(self):
        return self._sphere

    @property
    def tapped(self):
        return self._tapped

    def isTapped(self):
        return self.tapped

    def tap(self):
        self._tapped = True

    def unTap(self):
        self._tapped = False
