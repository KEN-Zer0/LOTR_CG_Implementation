from src.table import Table
from src.cards import *


table = Table()

# for quest in table.quest_deck:
#     print(quest.name)
print("Player Deck:")
for ally in table.player_deck:
    print(ally.name)

# for hero in table.player_heros:
#     print(hero.name)
print("\nEncounter Deck:")
for enemy in table.encounter_deck:
    if isinstance(enemy, Land):
        print("Location")
    else:
        print(enemy.name)

print(table.table_threat)