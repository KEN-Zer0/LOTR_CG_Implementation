from src.cards import *
from config import *

class Table:
    table_threat: int

    quest_deck: list[Quest]
    active_travel_location: Land

    player_deck: list[Hero, Ally]
    player_heros: list[Hero]
    player_hand: list[Ally]
    player_engagement: list[Hero, Ally]

    encounter_deck: list[Enemy]
    encounter_staging: list[Enemy]
    encounter_engagement: list[Enemy]

    def __init__(self):
        # import from deck
        self.quest_deck = []
        self.player_deck = []
        self.player_heros = []
        self.encounter_deck = all_cards_deck.encounter_deck.copy()

        self.calculate_table_threat()

    def calculate_table_threat(self):
        for hero in self.player_heros:
            self.table_threat += hero.threat