import argparse
from src.game.game import Game
from agents import RandomAgent, ExpertAgent

AGENTS = {
    "expert": ExpertAgent,
    "random": RandomAgent,
}

parser = argparse.ArgumentParser(description="LOTR Card Game")
parser.add_argument(
    "agent",
    nargs="?",
    default="expert",
    choices=AGENTS,
    help="Agent to use (default: expert)",
)
args = parser.parse_args()

game = Game(agent=AGENTS[args.agent]())
while not game.table.check_win_condition() and not game.table.check_lose_condition():
    game.run_round()

if game.table.check_win_condition():
    print("Victory! All quests completed.")
else:
    print("Defeat! The fellowship has fallen.")
