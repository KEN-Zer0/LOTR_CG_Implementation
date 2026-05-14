from src.cards.base_card import BaseCard


class Quest(BaseCard):
    def __init__(
            self,
            name,
            scenario,
            quest_points
    ):
        super().__init__(name)

        self._scenario = scenario
        self._points = quest_points

    @property
    def scenario(self):
        return self._scenario

    @property
    def quest_points(self):
        return self._points

    def change_points(self, deltaPoints):
        self._hitPoints += deltaPoints

    def copy(self):
        newQuest = Quest(
            self.name,
            self.scenario,
            self.quest_points
        )

        return newQuest
