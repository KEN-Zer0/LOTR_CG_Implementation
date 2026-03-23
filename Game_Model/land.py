from Game_Model.card import Card

class Land(Card):
    def __init__(self, id, name, threat, points):
        super(Land, self).__init__(id, name)
        self.threat = threat
        self.points = points
        self.defaultPoints = points

    def getThreat(self):
        return self.threat

    def getPoints(self):
        return self.points

    def setPoints(self, points):
        self.points = points

    def restoreDefaultPoints(self):
        self.points = self.defaultPoints

    def copy(self):
        newLand = Land(self.id, self.name, self.threat, self.points)
        return newLand

    def placeProgressTokens(self, progress):
        self.points -= progress
