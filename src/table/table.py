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

from agents import ExpertAgent


class Table:
    """Holds the full mutable game state shared by all phases."""

    def __init__(self, agent=None):
        """Initialize all decks, zones, and lists; calculate starting threat and shuffle decks.

        Args:
            agent: Decision-making strategy used by the phases. Defaults to ExpertAgent.
        """
        self.agent = agent if agent is not None else ExpertAgent()

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

        self.encounter_discard: list[Enemy | Location] = []

        self.calculate_table_threat()
        self.shuffle_decks()

    def calculate_table_threat(self):
        """Set table_threat to the sum of all hero threat values."""
        self.table_threat = 0

        for hero in self.player_heroes:
            self.table_threat += hero.threat

    def shuffle_decks(self):
        """Shuffle the player deck and encounter deck in place."""
        random.shuffle(self.player_deck)
        random.shuffle(self.encounter_deck)

    def draw_player_card(self):
        """Pop the top card of the player deck into the player's hand.

        Returns:
            Ally | None: The drawn card, or None if the player deck is empty.
        """
        if len(self.player_deck) == 0:
            return None

        card = self.player_deck.pop(0)

        self.player_hand.append(card)

        return card

    def reveal_encounter_card(self):
        """Pop the top encounter card into the staging area.

        When the encounter deck is empty the discard pile is reshuffled into it first.

        Returns:
            Enemy | Location | None: The revealed card, or None if both deck and discard are empty.
        """
        if len(self.encounter_deck) == 0:
            if not self.encounter_discard:
                return None
            self.encounter_deck = self.encounter_discard
            self.encounter_discard = []
            random.shuffle(self.encounter_deck)

        card = self.encounter_deck.pop(0)
        self.encounter_staging.append(card)
        return card

    def get_current_quest(self):
        """Return the top (active) quest card without removing it.

        Returns:
            Quest: The currently active quest card.
        """
        return self.quest_deck[0]

    def check_win_condition(self) -> bool:
        """Check whether the player has won the game.

        Returns:
            bool: True when the quest deck is empty (all quests completed).
        """
        return len(self.quest_deck) == 0

    def check_lose_condition(self) -> bool:
        """Check whether any losing condition has been triggered.

        Returns:
            bool: True when threat is too high or all heroes are dead.
        """
        return self.is_threat_too_high() or self.are_all_heroes_dead()

    def is_threat_too_high(self) -> bool:
        """Check whether the player's threat has reached the losing threshold.

        Returns:
            bool: True when table_threat has reached or exceeded LOSING_THREAT (50).
        """
        return self.table_threat >= GameConstants.LOSING_THREAT

    def are_all_heroes_dead(self) -> bool:
        """Check whether every hero has been defeated.

        Returns:
            bool: True when no hero in player_heroes is still alive.
        """
        for hero in self.player_heroes:
            if hero.is_alive():
                return False
        return True
