# main.py
from src.game.game import Game

game = Game()
while not game.table.check_lose_condition():
    game.run_round()
print("Game over")