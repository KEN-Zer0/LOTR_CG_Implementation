from .phase import Phase


class ResourcesPhase(Phase):
    def execute(self):
        self.increase_heros_resource()
        self.draw_one_card_from_player_deck()

    def increase_hero_resource(self, Hero):
        Hero.change_resource_pool(1)

    def increase_heros_resource(self):
        for hero in self.table.player_heros:
            self.increase_hero_resource(hero)

    def draw_one_card_from_player_deck(self):
        if len(self.table.player_deck) > 0:
            self.table.player_hand.append(self.table.player_deck.pop())