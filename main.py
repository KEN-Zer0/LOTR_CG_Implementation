from src.cards import BaseCard
from src.cards.creatures import Creature

from config.cards_dict import *

Gandalf = BaseCard('Gandalf')
Thorn = BaseCard('Thorn')

# print(Gandalf.name)
# print(Thorn.name)

Orc = Creature(Enemys.Dol_Guldur_Orcs, 1, 2, 3)
print(
    Orc.name,
    Orc.attack,
    Orc.defense,
    Orc.hitPoints
)

Orc.changeHitPoints(-3)

print(
    Orc.name,
    Orc.attack,
    Orc.defense,
    Orc.hitPoints
)