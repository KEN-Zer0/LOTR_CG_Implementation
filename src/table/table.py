from src.cards import *
from config import *
import random

class Table:
    table_threat: int = 0

    quest_deck: list[Quest]
    active_travel_location: Land | None = None

    player_deck: list[Ally]
    player_heros: list[Hero]
    player_hand: list[Ally]
    player_hand
    # 2 list for def and atk?
    player_engagement: list[Hero, Ally]

    encounter_deck: list[Enemy]
    encounter_staging: list[Enemy]
    encounter_engagement: list[Enemy]

    def __init__(self):
        self.quest_deck = all_cards_deck.quest_deck.copy()
        self.player_deck = all_cards_deck.player_deck.copy()
        self.player_heros = all_cards_deck.hero_pool.copy()
        self.encounter_deck = all_cards_deck.encounter_deck.copy()

        self.calculate_table_threat()
        self.shuffle_deck()

    def calculate_table_threat(self):
        for hero in self.player_heros:
            self.table_threat += hero.threat

    def shuffle_deck(self):
        random.shuffle(self.player_deck)
        random.shuffle(self.encounter_deck)