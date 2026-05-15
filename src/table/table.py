from src.cards import *
from config import *
import random

class Table:
    table_threat: int = 0

    quest_deck: list[Quest]
    active_travel_location: Land | None = None

    player_deck: list[Ally]
    player_heroes: list[Hero]
    player_hand: list[Ally]
    player_board: list[Ally]

    # make to dict in future
    player_engagement = [
        questing,
        attaking,
        defending
    ]

    encounter_deck: list[Enemy]
    encounter_staging: list[Enemy]
    encounter_engagement: list[Enemy]

    def __init__(self):
        self.quest_deck = all_cards_deck.quest_deck.copy()
        self.player_deck = all_cards_deck.player_deck.copy()
        self.player_heroes = all_cards_deck.hero_pool.copy()
        self.encounter_deck = all_cards_deck.encounter_deck.copy()

        self.calculate_table_threat()
        self.shuffle_deck()

    def calculate_table_threat(self):
        for hero in self.player_heroes:
            self.table_threat += hero.threat

    def shuffle_deck(self):
        random.shuffle(self.player_deck)
        random.shuffle(self.encounter_deck)

    def check_lose_condition(self):
        self.check_threat_level()
        self.check_heroes_alive()

    def check_threat_level(self):
        if self.table_threat >= 50:
            return True
        return False

    def check_heroes_alive(self):
        for hero in self.player_heroes:
            if hero.is_alive():
                return False
        return True