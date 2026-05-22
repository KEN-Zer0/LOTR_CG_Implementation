from src.cards.creatures.player_creatures import PlayerCreature


class Hero(PlayerCreature):
    def __init__(
            self,
            name,
            attack,
            defense,
            max_hit_points,
            willpower,
            sphere_of_influence,
            threat
    ):
        super().__init__(
            name,
            attack,
            defense,
            max_hit_points,
            willpower,
            sphere_of_influence
        )

        self._threat = threat
        self._resource_pool = 0

    @property
    def threat(self):
        return self._threat

    @property
    def resource_pool(self):
        return self._resource_pool

    def change_resource_pool(self, delta):
        self._resource_pool += delta

        if self._resource_pool < 0:
            self._resource_pool = 0

    def add_resource_token(self):
        self._resource_pool += 1

    def copy(self):
        new_hero = Hero(
            self.name,
            self.attack,
            self.defense,
            self.max_hit_points,
            self.willpower,
            self.sphere_of_influence,
            self.threat
        )

        new_hero._resource_pool = self._resource_pool
        return new_hero