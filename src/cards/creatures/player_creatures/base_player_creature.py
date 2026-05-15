from src.cards.creatures.base_creature import Creature


class PlayerCreature(Creature):
    def __init__(
            self,
            name,
            attack,
            defense,
            max_hit_points,
            willpower,
            sphere_of_influence
    ):
        super().__init__(
            name,
            attack,
            defense,
            max_hit_points
        )

        self._willpower = willpower
        self._sphere_of_influence = sphere_of_influence
        self._exhausted = False

    @property
    def willpower(self):
        return self._willpower

    @property
    def sphere_of_influence(self):
        return self._sphere_of_influence

    @property
    def exhausted(self):
        return self._exhausted

    def is_exhausted(self):
        return self._exhausted

    def exhaust(self):
        self._exhausted = True

    def ready(self):
        self._exhausted = False

    def is_alive(self):
        return self.hit_points() >= 0