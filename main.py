from src.table.table import Table
from src.cards import *
from src.game.phases import RefreshPhase

table = Table()

# # for quest in table.quest_deck:
# #     print(quest.name)
# print("Player Deck:")
# for ally in table.player_deck:
#     print(ally.name)
#
# # for hero in table.player_heros:
# #     print(hero.name)
# print("\nEncounter Deck:")
# for enemy in table.encounter_deck:
#     if isinstance(enemy, Land):
#         print("Location")
#     else:
#         print(enemy.name)

print(table.table_threat)

RefreshPhase(table).execute()
print(table.table_threat)