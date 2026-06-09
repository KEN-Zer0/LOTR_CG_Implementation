from src.game.phases import *
from src.table import *


class Game:
    """Orchestrates the seven game phases for each round until win or lose condition is met."""

    def __init__(self):
        """Initialize the table and the ordered list of game phases."""
        self.table = Table()

        self.phases = [
            ResourcesPhase(self.table),
            PlanningPhase(self.table),
            QuestPhase(self.table),
            TravelPhase(self.table),
            EncounterPhase(self.table),
            CombatPhase(self.table),
            RefreshPhase(self.table)
        ]

    def run_round(self):
        """Execute each phase in order, stopping early if the game ends mid-round."""
        for phase in self.phases:
            if self.table.check_win_condition() or self.table.check_lose_condition():
                return
            phase.execute()
