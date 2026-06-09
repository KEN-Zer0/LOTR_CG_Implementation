from src.cards.creatures.player_creatures import PlayerCreature


class Hero(PlayerCreature):
    """Player-controlled hero with a fixed threat cost and a resource pool."""

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
        """Initialize hero; resource_pool starts at 0."""
        super().__init__(name, attack, defense, max_hit_points, willpower, sphere_of_influence)

        self._threat = threat
        self._resource_pool = 0

    @property
    def threat(self):
        """Starting-threat contribution added to the player's threat total at game start."""
        return self._threat

    @property
    def resource_pool(self):
        """Current number of resource tokens available for paying card costs."""
        return self._resource_pool

    def change_resource_pool(self, delta):
        """Add delta to resource_pool, floored at 0."""
        self._resource_pool += delta

        if self._resource_pool < 0:
            self._resource_pool = 0

    def add_resource_token(self):
        """Increase resource_pool by 1 (shortcut for change_resource_pool(1))."""
        self._resource_pool += 1

    def copy(self):
        """Return a new Hero with identical stats and the same current resource_pool."""
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
