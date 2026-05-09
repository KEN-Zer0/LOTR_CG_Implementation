from src.cards import *

from enum import Enum, unique


@unique
class Heroes(Enum):
    Eowyn = 1
    Eleaonr = 2
    Thalin = 3


@unique
class Allies(Enum):
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
    Flies_and_Spiders = 1
    A_fork_in_the_road = 2
    Beorns_Path = 3


@unique
class Enemys(Enum):
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
class Land(Enum):
    Great_Forest_Web = 1
    Mountains_of_Mirkwood = 2
    Necromancers_Pass = 3
    Enchanted_Stream = 4
    Old_Forest_Road = 5
    Forest_Gate = 6
