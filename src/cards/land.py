from src.cards.base_card import BaseCard


class Land(BaseCard):
    def __init__(self, name, threat, points):
        super(Land, self).__init__(name)
        self._threat = threat
        self._points = points

    @property
    def threat(self):
        return self._threat

    @property
    def points(self):
        return self._points

    def changePoints(self, deltaPoints):
        self._hitPoints += deltaPoints

    def isComplete(self):
        return self._points <= 0

    def copy(self):
        newLand = Land(
            self.name,
            self.threat,
            self.points
        )

        return newLand
