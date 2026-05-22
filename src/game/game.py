from src.game.phases import *


class Game:

    def __init__(self):
        self.table = Table()

        self.phases = [
            ResourcePhase(self.table),
            PlanningPhase(self.table),
            QuestPhase(self.table),
            TravelPhase(self.table),
            EncounterPhase(self.table),
            CombatPhase(self.table),
            RefreshPhase(self.table)
        ]

    def run_round(self):
        for phase in self.phases:
            phase.execute()
