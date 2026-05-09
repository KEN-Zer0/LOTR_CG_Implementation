from src.cards.base_card import BaseCard


class Quest(BaseCard):
    def __init__(
            self,
            name,
            scenario,
            points
    ):
        super().__init__(name)

        self._scenario = scenario
        self._points = points

    @property
    def scenario(self):
        return self._scenario

    @property
    def points(self):
        return self._points

    def changePoints(self, deltaPoints):
        self._hitPoints += deltaPoints

    def copy(self):
        newQuest = Quest(
            self.name,
            self.scenario,
            self.points
        )

        return newQuest
