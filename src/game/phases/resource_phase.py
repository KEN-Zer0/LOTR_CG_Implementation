from src.table import Table
from .phase import Phase


class ResourcesPhase(Phase):

    def executePhase(self):
        self.increase_heros_resource()

    def increase_hero_resource(self, Hero):
        Hero.change_resource_pool(1)

    def increase_heros_resource(self):
        for hero in self._table.player_heros:
            self.increase_hero_resource(hero)

    def draw_one_card_from_player_deck(self):

        pass