from .phase import Phase
from config import *

class PlanningPhase(Phase):
    def execute(self):
        while True:
            available_cards= [
                card for card in self.table.player_hand
                if self.table.can_pay_for(card)
            ]

            if not available_cards:
                break

            choice = input(
                "Choose card index or 'pass': "
            )

            if choice == "pass":
                break

            try:
                card = available_cards[int(choice)]

                self.play_card(card)

            except (
                    ValueError,
                    IndexError
            ):
                print("Invalid choice")

    def play_card(self, card):

        self.table.pay_for_card(card)

        self.table.player_hand.remove(card)

        self.table.player_board.append(card)

        print(f"Played: {card.name}")