from src.cards.base_card import BaseCard


class Land(BaseCard):
    def __init__(
            self,
            name,
            threat,
            quest_points
    ):
        super().__init__(name)

        self._threat = threat
        self._points = quest_points

    @property
    def threat(self):
        return self._threat

    @property
    def quest_points(self):
        return self._points

    def change_points(self, deltaPoints):
        self._hitPoints += deltaPoints

    def is_complete(self):
        return self._points <= 0

    def copy(self):
        return Land(
            self.name,
            self.threat,
            self.quest_points
        )
