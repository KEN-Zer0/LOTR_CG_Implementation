"""Deck composition for the Passage through Mirkwood scenario.

Modify which cards appear (and how many copies) here.
Card stats live in cards_registry.py — do not duplicate them here.
"""

from config.limited.cards_list import Heroes, Allies, Enemies, Locations, Quests, Scenario
from config.limited.cards_registry import CARDS

hero_pool = [
    CARDS[Heroes.Eowyn].copy(),
    CARDS[Heroes.Eleanor].copy(),
    CARDS[Heroes.Thalin].copy(),
]

encounter_deck = [
    CARDS[Enemies.Dol_Guldur_Orcs].copy(),
    CARDS[Enemies.Chieftan_Ufthak].copy(),
    CARDS[Enemies.Dol_Guldur_Beastmaster].copy(),
    CARDS[Enemies.Forest_Spider].copy(),
    CARDS[Enemies.East_Bight_Patrol].copy(),
    CARDS[Enemies.Black_Forest_Bats].copy(),
    CARDS[Enemies.King_Spider].copy(),
    CARDS[Enemies.Hummerhorns].copy(),
    CARDS[Enemies.Ungoliants_Spawn].copy(),
    CARDS[Locations.Necromancers_Pass].copy(),
    CARDS[Locations.Enchanted_Stream].copy(),
    CARDS[Locations.Old_Forest_Road].copy(),
    CARDS[Locations.Forest_Gate].copy(),
    CARDS[Locations.Great_Forest_Web].copy(),
    CARDS[Locations.Mountains_of_Mirkwood].copy(),
]

player_deck = [
    CARDS[Allies.Wandering_Took].copy(),
    CARDS[Allies.Lorien_Guide].copy(),
    CARDS[Allies.Northern_Tracker].copy(),
    CARDS[Allies.Veteran_Axehand].copy(),
    CARDS[Allies.Gondorian_Spearman].copy(),
    CARDS[Allies.Horseback_Archer].copy(),
    CARDS[Allies.Beorn].copy(),
    CARDS[Allies.Gandalf].copy(),
]

quest_deck = [
    CARDS[Quests.Flies_and_Spiders].copy(),
    CARDS[Quests.A_fork_in_the_road].copy(),
    CARDS[Quests.Beorns_Path].copy(),
]
