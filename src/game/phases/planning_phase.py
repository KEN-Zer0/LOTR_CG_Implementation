from .phase import Phase
from src.cards import Hero, Ally


class PlanningPhase(Phase):
    """
    Planning phase — player plays Ally cards from hand onto the board.

    The player can play any number of cards as long as they can pay the cost.
    Resources are distributed across heroes. Payment pulls from the hero
    with the most resources first. The phase ends when no affordable cards
    remain or the player chooses to pass.
    """

    def execute(self):
        while True:
            playable = self._get_playable_cards()
            if not playable:
                break

            card = self._choose_card(playable)
            if card is None:
                break

            self._play_card(card)

    def _get_playable_cards(self) -> list[Ally]:
        """Returns cards in hand that the player can currently afford."""
        return [
            card for card in self.table.player_hand
            if self._total_resources() >= card.cost
        ]

    def _total_resources(self) -> int:
        """Returns the sum of resource pools across all heroes."""
        return sum(hero.resource_pool for hero in self.table.player_heroes)

    def _choose_card(self, playable: list[Ally]) -> Ally | None:
        """
        Selects a card to play from the list of affordable cards.

        Override this method to implement custom selection logic,
        e.g. for an AI agent. Returns None to pass.
        Default: plays the cheapest card.
        """
        return min(playable, key=lambda card: card.cost)

    def _play_card(self, card: Ally) -> None:
        """Pays for the card, moves it from hand to the player board."""
        self._pay_for_card(card)
        self.table.player_hand.remove(card)
        self.table.player_board.append(card)

    def _pay_for_card(self, card: Ally) -> None:
        """
        Deducts the card cost from hero resource pools.
        Heroes with the most resources are spent first.
        """
        remaining = card.cost

        for hero in sorted(self.table.player_heroes, key=lambda h: h.resource_pool, reverse=True):
            if remaining <= 0:
                break
            paid = min(hero.resource_pool, remaining)
            hero.change_resource_pool(-paid)
            remaining -= paid