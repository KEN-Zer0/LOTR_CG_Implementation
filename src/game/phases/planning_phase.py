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
        """Play affordable Ally cards from hand until none remain or the player passes."""
        while True:
            playable = self._get_playable_cards()
            if not playable:
                break

            card = self._choose_card(playable)
            if card is None:
                break

            self._play_card(card)

    def _get_playable_cards(self) -> list[Ally]:
        """Return cards in hand whose cost the player can currently afford.

        Returns:
            list[Ally]: Affordable cards from the player's hand.
        """
        return [
            card for card in self.table.player_hand
            if self._total_resources() >= card.cost
        ]

    def _total_resources(self) -> int:
        """Return the sum of resource pools across all heroes.

        Returns:
            int: Total resources available to spend this phase.
        """
        return sum(hero.resource_pool for hero in self.table.player_heroes)

    def _choose_card(self, playable: list[Ally]) -> Ally | None:
        """Delegates to the table's agent.

        Args:
            playable (list[Ally]): Cards that the player can currently afford.

        Returns:
            Ally | None: The card to play, or None to pass.
        """
        return self.table.agent.choose_card_to_play(self.table, playable)

    def _play_card(self, card: Ally) -> None:
        """Pay for the card and move it from hand to the player board.

        Args:
            card (Ally): The card to play.
        """
        self._pay_for_card(card)
        self.table.player_hand.remove(card)
        self.table.player_board.append(card)

    def _pay_for_card(self, card: Ally) -> None:
        """Deduct the card cost from hero resource pools (highest-resource hero first).

        Args:
            card (Ally): The card whose cost is being paid.
        """
        remaining = card.cost

        for hero in sorted(self.table.player_heroes, key=lambda h: h.resource_pool, reverse=True):
            if remaining <= 0:
                break
            paid = min(hero.resource_pool, remaining)
            hero.change_resource_pool(-paid)
            remaining -= paid