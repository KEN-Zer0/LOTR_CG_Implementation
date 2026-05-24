from .phase import Phase


class ResourcesPhase(Phase):
    def execute(self):
        self.increase_heroes_resource()
        self.draw_one_card_from_player_deck()

    def increase_hero_resource(self, hero):
        hero.change_resource_pool(1)

    def increase_heroes_resource(self):
        for hero in self.table.player_heroes:
            self.increase_hero_resource(hero)

    def draw_one_card_from_player_deck(self):
        self.table.draw_player_card()
