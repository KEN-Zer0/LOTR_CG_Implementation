from src.cards.creatures.base_creature import Creature


class PlayerCreature(Creature):
    def __init__(
            self,
            name,
            attack,
            defense,
            max_hit_points,
            willpower,
            sphere
    ):
        super().__init__(
            name,
            attack,
            defense,
            max_hit_points
        )

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

    def is_tapped(self):
        return self._tapped

    def tap(self):
        self._tapped = True

    def untap(self):
        self._tapped = False