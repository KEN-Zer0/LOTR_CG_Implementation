import random

from config import all_cards_deck
from config.constants import GameConstants, PlayerEngagementType

from src.cards import (
    Hero,
    Ally,
    Enemy,
    Quest,
    Location
)


class Table:

    def __init__(self):

        self.table_threat = 0

        # QUEST

        self.quest_deck: list[Quest] = (
            all_cards_deck.quest_deck.copy()
        )

        self.active_travel_location: Location | None = None

        # PLAYER

        self.player_deck: list[Ally] = (
            all_cards_deck.player_deck.copy()
        )

        self.player_heroes: list[Hero] = (
            all_cards_deck.hero_pool.copy()
        )

        self.player_hand: list[Ally] = []

        self.player_board: list[Ally] = []

        # QUESTING / COMBAT

        self.questing: list[Hero | Ally] = []

        self.attacking: list[Hero | Ally] = []

        self.defending: list[Hero | Ally] = []

        self.player_engagement = {
            PlayerEngagementType.QUESTING: self.questing,
            PlayerEngagementType.ATTACKING: self.attacking,
            PlayerEngagementType.DEFENDING: self.defending
        }

        # ENCOUNTER

        self.encounter_deck: list[Enemy | Location] = (
            all_cards_deck.encounter_deck.copy()
        )

        self.encounter_staging: list[Enemy | Location] = []

        self.encounter_engagement: list[Enemy] = []

        self.calculate_table_threat()
        self.shuffle_decks()

    def calculate_table_threat(self):

        self.table_threat = 0

        for hero in self.player_heroes:
            self.table_threat += hero.threat

    def shuffle_decks(self):

        random.shuffle(self.player_deck)
        random.shuffle(self.encounter_deck)

    def draw_player_card(self):

        if len(self.player_deck) == 0:
            return None

        card = self.player_deck.pop(0)

        self.player_hand.append(card)

        return card

    def reveal_encounter_card(self):

        if len(self.encounter_deck) == 0:
            return None

        card = self.encounter_deck.pop(0)

        self.encounter_staging.append(card)

        return card

    def get_current_quest(self):

        return self.quest_deck[0]

    def check_lose_condition(self):

        if self.check_threat_level():
            return True

        if self.check_heroes_alive():
            return True

        return False

    def check_threat_level(self):

        return self.table_threat >= GameConstants.LOSING_THREAT

    def check_heroes_alive(self):

        for hero in self.player_heroes:

            if hero.is_alive():
                return False

        return True
