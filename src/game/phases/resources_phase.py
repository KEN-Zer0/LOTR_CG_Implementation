from .phase import Phase


class ResourcesPhase(Phase):
    def execute(self):
        self.increase_heroes_resource()

    def increase_hero_resource(self, Hero):
        Hero.change_resource_pool(1)

    def increase_heroes_resource(self):
        for hero in self._table.player_heroes:
            self.increase_hero_resource(hero)