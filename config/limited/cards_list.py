"""Enum identifiers for every card, sphere, and scenario in the game."""

from src.cards import *

from enum import Enum, unique


@unique
class Heroes(Enum):
    """Unique identifiers for all hero cards."""

    Eowyn = 1
    Eleanor = 2
    Thalin = 3


@unique
class Allies(Enum):
    """Unique identifiers for all ally cards."""

    Wandering_Took = 1
    Lorien_Guide = 2
    Northern_Tracker = 3
    Veteran_Axehand = 4
    Gondorian_Spearman = 5
    Horseback_Archer = 6
    Beorn = 7
    Gandalf = 8


@unique
class Quests(Enum):
    """Unique identifiers for all quest cards."""

    Flies_and_Spiders = 1
    A_fork_in_the_road = 2
    Beorns_Path = 3


@unique
class Enemies(Enum):
    """Unique identifiers for all enemy cards."""

    Dol_Guldur_Orcs = 1
    Chieftan_Ufthak = 2
    Dol_Guldur_Beastmaster = 3
    Forest_Spider = 4
    East_Bight_Patrol = 5
    Black_Forest_Bats = 6
    King_Spider = 7
    Hummerhorns = 8
    Ungoliants_Spawn = 9


@unique
class Locations(Enum):
    """Unique identifiers for all location cards."""

    Great_Forest_Web = 1
    Mountains_of_Mirkwood = 2
    Necromancers_Pass = 3
    Enchanted_Stream = 4
    Old_Forest_Road = 5
    Forest_Gate = 6


@unique
class Sphere(Enum):
    """Resource spheres that determine which heroes can pay for a card."""

    Spirit = 1
    Tactics = 2
    Neutral = 3


@unique
class Scenario(Enum):
    """Identifiers for available scenario campaigns."""

    Passage_through_Mirkwood = 1
