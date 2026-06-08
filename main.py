# main.py
from src.game.game import Game

game = Game()
while not game.table.check_win_condition() and not game.table.check_lose_condition():
    game.run_round()

if game.table.check_win_condition():
    print("Victory! All quests completed.")
else:
    print("Defeat! The fellowship has fallen.")
