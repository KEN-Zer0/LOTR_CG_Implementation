from config.cards_list import Enemys
from config.cards_list import Lands
from src.cards.creatures import player_creatures
from src.cards.creatures.enemy import Enemy
from src.cards.land import Land

# * - not implemented
# player_deck=[] # ally, attachement*, event*
# encounter_deck=[] # Enemy, location (land) , trachery*, objective*
# quest_deck=[]  # Quest

# hero_pool=[] #Hero ! not random



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
