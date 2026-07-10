from .phase import Phase
from config.constants import GameConstants
from src.cards import Hero


class ResourcesPhase(Phase):
    """Phase 1 — each hero gains 1 resource token and the player draws 1 card."""

    def execute(self) -> None:
        """Grant 1 resource to every hero and draw one card from the player deck."""
        self.increase_heroes_resource()
        self.draw_one_card_from_player_deck()

    def increase_hero_resource(self, hero: Hero) -> None:
        """Add 1 resource token to the given hero."""
        hero.change_resource_pool(GameConstants.RESOURCES_PER_HERO_PER_ROUND)

    def increase_heroes_resource(self) -> None:
        """Add 1 resource token to each hero in the player's party."""
        for hero in self.table.player_heroes:
            self.increase_hero_resource(hero)

    def draw_one_card_from_player_deck(self) -> None:
        """Draw one card from the player deck into the player's hand."""
        self.table.draw_player_card()
