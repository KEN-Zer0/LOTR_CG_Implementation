import argparse
from src.game.game import Game
from agents import RandomAgent, ExpertAgent

VICTORY_MSG   = "Victory! All quests completed."
THREAT_DEFEAT = "Defeat! Threat reached 50."
HEROES_DEFEAT = "Defeat! All heroes are dead."

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
if is_victory:
    print(VICTORY_MSG)
elif game.table.is_threat_too_high():
    print(THREAT_DEFEAT)
else:
    print(HEROES_DEFEAT)

if args.log or args.logfile:
    game.log_summary(is_victory)
    Logger.close()
