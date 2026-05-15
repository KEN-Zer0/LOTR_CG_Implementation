from .phase import Phase


class ResourcesPhase(Phase):
    def executePhase(self):
        increase_heros_resource()

    def increase_hero_resource(self, Hero):
        Hero.change_resource_pool(1)

    def increase_heros_resource(self):
        for hero in self._table.player_heroes:
            increase_hero_resource(hero)