from src.cards import *
from config import *
from config.constants import LOSING_THREAT
import random


class Table:
    table_threat: int = 0

    quest_deck: list[Quest] = all_cards_deck.quest_deck.copy()
    active_travel_location: Location | None = None

    player_deck: list[Ally] = all_cards_deck.player_deck.copy()
    player_heroes: list[Hero] = all_cards_deck.hero_pool.copy()
    player_hand: list[Ally]
    player_boarqd: list[Ally]

    # make to dict in future
    questing: list[Ally, Hero] = []
    attacking: list[Ally, Hero] = []
    defending: list[Ally, Hero] = []
    player_engagement = [
        questing,
        attacking,
        defending
    ]

    encounter_deck: list[Enemy] = all_cards_deck.encounter_deck.copy()
    encounter_staging: list[Enemy]
    encounter_engagement: list[Enemy]

    def __init__(self):
        # self.quest_deck = all_cards_deck.quest_deck.copy()
        # self.player_deck = all_cards_deck.player_deck.copy()
        # self.player_heroes = all_cards_deck.hero_pool.copy()
        # self.encounter_deck = all_cards_deck.encounter_deck.copy()

        self.calculate_table_threat()
        self.shuffle_deck()

    def calculate_table_threat(self):
        for hero in self.player_heroes:
            self.table_threat += hero.threat

    def shuffle_deck(self):
        random.shuffle(self.player_deck)
        random.shuffle(self.encounter_deck)

    def check_lose_condition(self):
        if self.check_threat_level():
            print("Game Over")
        if self.check_heroes_alive():
            print("Game Over")

    def check_threat_level(self):
        if self.table_threat >= LOSING_THREAT:
            return True
        return False

    def check_heroes_alive(self):
        for hero in self.player_heroes:
            if hero.is_alive():
                return False
        return True
