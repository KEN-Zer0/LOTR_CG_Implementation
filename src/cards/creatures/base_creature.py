from src.cards.base_card import BaseCard


class Creature(BaseCard):
    def __init__(
            self,
            name,
            attack,
            defense,
            max_hit_points
    ):
        super().__init__(name)

        self._attack = attack
        self._defense = defense
        self._max_hit_points = max_hit_points
        self._hit_points = max_hit_points

    @property
    def attack(self):
        return self._attack

    @property
    def defense(self):
        return self._defense

    @property
    def max_hit_points(self):
        return self._max_hit_points

    @property
    def hit_points(self):
        return self._hit_points

    def is_dead(self):
        return self._hit_points <= 0

    def change_hp(self, delta_hp):
        self._hit_points += delta_hp

        if self._hit_points > self._max_hit_points:
            self._hit_points = self._max_hit_points

        if self._hit_points < 0:
            self._hit_points = 0