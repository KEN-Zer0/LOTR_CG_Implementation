from .phase import Phase
from src.cards import Hero, Ally
from config.limited.cards_list import Sphere


class PlanningPhase(Phase):
    """
    Planning phase — player plays Ally cards from hand onto the board.

    The player can play any number of cards as long as they can pay the cost.
    Resources are distributed across heroes. Payment pulls from the hero
    with the most resources first. The phase ends when no affordable cards
    remain or the player chooses to pass.
    """

    def execute(self) -> None:
        """Play affordable Ally cards from hand until none remain or the player passes."""
        shown = False
        while True:
            playable = self._get_playable_cards()
            if not playable:
                if not shown:
                    self._choose_card(playable)
                break

            shown = True
            card = self._choose_card(playable)
            if card is None:
                break

            self._play_card(card)

    def _get_playable_cards(self) -> list[Ally]:
        """Return cards in hand whose cost the player can currently afford within the matching sphere.

        Returns:
            list[Ally]: Affordable cards from the player's hand.
        """
        return [
            card for card in self.table.player_hand
            if self._resources_for_sphere(card.sphere_of_influence) >= card.cost
        ]

    def _heroes_for_sphere(self, sphere: Sphere) -> list[Hero]:
        """Return heroes that can contribute resources for a given sphere.

        Neutral cards can be paid by any hero regardless of sphere.

        Args:
            sphere: The sphere to match.

        Returns:
            list: Heroes whose resources are valid for paying the sphere cost.
        """
        if sphere == Sphere.Neutral:
            return list(self.table.player_heroes)
        return [h for h in self.table.player_heroes if h.sphere_of_influence == sphere]

    def _resources_for_sphere(self, sphere: Sphere) -> int:
        """Return the sum of resource pools for heroes eligible to pay for a given sphere.

        Args:
            sphere: The sphere to match.

        Returns:
            int: Total resources available for that sphere.
        """
        return sum(hero.resource_pool for hero in self._heroes_for_sphere(sphere))

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
        """Deduct the card cost from heroes of the matching sphere (highest-resource first).

        Args:
            card (Ally): The card whose cost is being paid.
        """
        remaining = card.cost

        for hero in sorted(self._heroes_for_sphere(card.sphere_of_influence), key=lambda h: h.resource_pool, reverse=True):
            if remaining <= 0:
                break
            paid = min(hero.resource_pool, remaining)
            hero.change_resource_pool(-paid)
            remaining -= paid