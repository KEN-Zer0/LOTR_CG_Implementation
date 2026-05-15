from game.phases import *

class PlanningPhase(Phase):
    # gracz może kupic kartę. frakcje mają własne waluty i za daną walute można kupić waluty
    def executePhase(self):
        super().executePhase()

    def buy_card(self):
        pass