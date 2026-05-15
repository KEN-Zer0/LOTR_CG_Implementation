from config.cards_list import *

from src.cards import *

# * - not implemented
# player_deck=[] # ally, attachement*, event*
# encounter_deck=[] # Enemy, location (land) , trachery*, objective*
# quest_deck=[]  # Quest

### TODO:
# Divide each deck into a separate file
# Separate Enums, lists, dictionaries
# Make some easy to use system for changing decks,
# need to have duplicates related utilities

hero_pool = [
    Hero(Heroes.Eowyn, 1, 1, 3, 4, Sphere.Spirit, 9),
    Hero(Heroes.Eleanor, 1, 2, 3, 1, Sphere.Spirit, 7),
    Hero(Heroes.Thalin, 2, 2, 4, 1, Sphere.Tactics, 9)
]  # Hero ! not random

encounter_deck = [
    Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2),
    Enemy(Enemies.Chieftan_Ufthak, 3, 3, 6, 35, 2),
    Enemy(Enemies.Dol_Guldur_Beastmaster, 3, 1, 5, 35, 2),
    Enemy(Enemies.Forest_Spider, 2, 1, 4, 25, 2),
    Enemy(Enemies.East_Bight_Patrol, 3, 1, 2, 5, 3),
    Enemy(Enemies.Black_Forest_Bats, 1, 0, 2, 15, 1),
    Enemy(Enemies.King_Spider, 3, 1, 3, 20, 2),
    Enemy(Enemies.Hummerhorns, 2, 0, 3, 40, 1),
    Enemy(Enemies.Ungoliants_Spawn, 5, 2, 9, 32, 3),

    Land(Lands.Necromancers_Pass, 3, 2),
    Land(Lands.Enchanted_Stream, 2, 2),
    Land(Lands.Old_Forest_Road, 1, 3),
    Land(Lands.Forest_Gate, 2, 4),
    Land(Lands.Great_Forest_Web, 2, 2),
    Land(Lands.Mountains_of_Mirkwood, 2, 3)
]

player_deck = [  # for now there are only one card of each name (enum value)
    Ally(Allies.Wandering_Took, 1, 1, 2, 1, Sphere.Spirit, 2),
    Ally(Allies.Lorien_Guide, 1, 1, 2, 0, Sphere.Spirit, 3),
    Ally(Allies.Northern_Tracker, 2, 2, 3, 1, Sphere.Spirit, 4),
    Ally(Allies.Veteran_Axehand, 2, 1, 2, 0, Sphere.Tactics, 2),
    Ally(Allies.Gondorian_Spearman, 1, 1, 1, 0, Sphere.Tactics, 2),
    Ally(Allies.Horseback_Archer, 2, 1, 2, 0, Sphere.Tactics, 3),
    Ally(Allies.Beorn, 3, 3, 6, 1, Sphere.Tactics, 6),
    Ally(Allies.Gandalf, 4, 4, 4, 4, Sphere.Neutral, 5)
]

quest_deck = [
    Quest(Quests.Flies_and_Spiders, Scenario.Passage_through_Mirkwood, 8),
    Quest(Quests.A_fork_in_the_road, Scenario.Passage_through_Mirkwood, 2),
    Quest(Quests.Beorns_Path, Scenario.Passage_through_Mirkwood, 10)
]

all_cards_dict = {  # cards that can occur more than once in a deck
    Allies.Wandering_Took: Ally(Allies.Wandering_Took, 1, 1, 2, 1, Sphere.Spirit, 2),
    Allies.Lorien_Guide: Ally(Allies.Lorien_Guide, 1, 1, 2, 0, Sphere.Spirit, 3),
    Allies.Northern_Tracker: Ally(Allies.Northern_Tracker, 2, 2, 3, 1, Sphere.Spirit, 4),
    Allies.Veteran_Axehand: Ally(Allies.Veteran_Axehand, 2, 1, 2, 0, Sphere.Tactics, 2),
    Allies.Gondorian_Spearman: Ally(Allies.Gondorian_Spearman, 1, 1, 1, 0, Sphere.Tactics, 2),
    Allies.Horseback_Archer: Ally(Allies.Horseback_Archer, 2, 1, 2, 0, Sphere.Tactics, 3),
    Allies.Beorn: Ally(Allies.Beorn, 3, 3, 6, 1, Sphere.Tactics, 6),
    Allies.Gandalf: Ally(Allies.Gandalf, 4, 4, 4, 4, Sphere.Neutral, 5),

    Enemies.Dol_Guldur_Orcs: Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2),
    Enemies.Chieftan_Ufthak: Enemy(Enemies.Chieftan_Ufthak, 3, 3, 6, 35, 2),
    Enemies.Dol_Guldur_Beastmaster: Enemy(Enemies.Dol_Guldur_Beastmaster, 3, 1, 5, 35, 2),
    Enemies.Forest_Spider: Enemy(Enemies.Forest_Spider, 2, 1, 4, 25, 2),
    Enemies.East_Bight_Patrol: Enemy(Enemies.East_Bight_Patrol, 3, 1, 2, 5, 3),
    Enemies.Black_Forest_Bats: Enemy(Enemies.Black_Forest_Bats, 1, 0, 2, 15, 1),
    Enemies.King_Spider: Enemy(Enemies.King_Spider, 3, 1, 3, 20, 2),
    Enemies.Hummerhorns: Enemy(Enemies.Hummerhorns, 2, 0, 3, 40, 1),
    Enemies.Ungoliants_Spawn: Enemy(Enemies.Ungoliants_Spawn, 5, 2, 9, 32, 3),

    Lands.Necromancers_Pass: Land(Lands.Necromancers_Pass, 3, 2),
    Lands.Enchanted_Stream: Land(Lands.Enchanted_Stream, 2, 2),
    Lands.Old_Forest_Road: Land(Lands.Old_Forest_Road, 1, 3),
    Lands.Forest_Gate: Land(Lands.Forest_Gate, 2, 4),
    Lands.Great_Forest_Web: Land(Lands.Great_Forest_Web, 2, 2),
    Lands.Mountains_of_Mirkwood: Land(Lands.Mountains_of_Mirkwood, 2, 3)
}
