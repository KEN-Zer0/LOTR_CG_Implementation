import argparse
from src.game.game import Game
from agents import RandomAgent, ExpertAgent

VICTORY_MSG = "Victory! All quests completed."
DEFEAT_MSG  = "Defeat! The fellowship has fallen."

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
parser.add_argument(
    "--log", "-l",
    action="store_true",
    help="Enable verbose logging to stdout",
)
parser.add_argument(
    "--logfile", "-lf",
    action="store_true",
    help="Enable verbose logging to logs/game-log-{id}-{date}.txt",
)
args = parser.parse_args()

agent = AGENTS[args.agent]()

if args.log or args.logfile:
    from logger import Logger, default_log_path
    from agents.logging_agent import LoggingAgent
    from src.game.logging_game import LoggingGame

    Logger.enable(file_path=default_log_path() if args.logfile else None)
    game = LoggingGame(agent=LoggingAgent(agent))
else:
    game = Game(agent=agent)

while not game.table.check_win_condition() and not game.table.check_lose_condition():
    game.run_round()

is_victory = game.table.check_win_condition()
print(VICTORY_MSG if is_victory else DEFEAT_MSG)

if args.log or args.logfile:
    game.log_summary(is_victory)
    Logger.close()
