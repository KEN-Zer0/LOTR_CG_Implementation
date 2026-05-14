from config.cards_list import Heroes
from config.cards_list import Enemys
from config.cards_list import Lands
from config.cards_list import Allies
from config.cards_list import Quests

from src.cards.creatures.enemy import Enemy
from src.cards.land import Land
from src.cards.quest import Quest
from src.cards.creatures.player_creatures.hero import Hero
from src.cards.creatures.player_creatures.ally import Ally

# * - not implemented
# player_deck=[] # ally, attachement*, event*
# encounter_deck=[] # Enemy, location (land) , trachery*, objective*
# quest_deck=[]  # Quest

hero_pool=[
   Hero(Heroes.Eowyn, 1, 1, 3, 4, 'Spirit', 9),
   Hero(Heroes.Eleanor, 1, 2, 3, 1, 'Spirit', 7),
   Hero(Heroes.Thalin, 2, 2, 4, 1, 'Tactics', 9)
] #Hero ! not random



encounter_deck = [
    # UWAGA! Pominięto parametr hitMaxPoints!
    Enemy(Enemys.Dol_Guldur_Orcs, 2, 0, 3, 10, 2),
    Enemy(Enemys.Chieftan_Ufthak, 3, 3, 6, 35, 2),
    Enemy(Enemys.Dol_Guldur_Beastmaster, 3, 1, 5, 35, 2),
    Enemy(Enemys.Forest_Spider, 2, 1, 4, 25, 2),
    Enemy(Enemys.East_Bight_Patrol, 3, 1, 2, 5, 3),
    Enemy(Enemys.Black_Forest_Bats, 1, 0, 2, 15, 1),
    Enemy(Enemys.King_Spider, 3, 1, 3, 20, 2),
    Enemy(Enemys.Hummerhorns, 2, 0, 3, 40, 1),
    Enemy(Enemys.Ungoliants_Spawn, 5, 2, 9, 32, 3),

    Land(Lands.Necromancers_Pass, 3, 2),
    Land(Lands.Enchanted_Stream, 2, 2),
    Land(Lands.Old_Forest_Road, 1, 3),
    Land(Lands.Forest_Gate, 2, 4),
    Land(Lands.Great_Forest_Web, 2, 2),
    Land(Lands.Mountains_of_Mirkwood, 2, 3)
]


player_deck=[
    Ally(Allies.Wandering_Took, 1, 1, 2, 1, 'Spirit', 2),
    Ally(Allies.Lorien_Guide, 1, 1, 2, 0, 'Spirit', 3),
    Ally(Allies.Northern_Tracker, 2, 2, 3, 1, 'Spirit', 4),
    Ally(Allies.Veteran_Axehand, 2, 1, 2, 0, 'Tactics', 2),
    Ally(Allies.Gondorian_Spearman, 1, 1, 1, 0, 'Tactics', 2),
    Ally(Allies.Horseback_Archer, 2, 1, 2, 0, 'Tactics', 3),
    Ally(Allies.Beorn, 3, 3, 6, 1, 'Tactics', 6),
    Ally(Allies.Gandalf, 4, 4, 4, 4, 'Neutral', 5)
]

quest_deck=[
    Quest(Quests.Flies_and_Spiders, 'Passage through Mirkwood', 8),
    Quest(Quests.A_fork_in_the_road, 'Passage through Mirkwood', 2),
    Quest(Quests.Beorns_Path, 'Passage through Mirkwood', 10)
]
