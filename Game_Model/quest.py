from Game_Model.card import Card

class Quest(Card):
    def __init__(self, id, name, scenario, points):
        super(Quest, self).__init__(id, name)
        self.scenario = scenario
        self.points = points
        self.defaultPoints = points

    def copy(self):
        newQuest = Quest(self.id, self.name, self.scenario, self.points)
        return newQuest

    def getScenario(self):
        return self.scenario

    def getPoints(self):
        return self.points

    def setPoints(self, points):
        self.points = points

    def restoreDefaultPoints(self):
        self.points = self.defaultPoints

    def placeProgressTokens(self, progress):
        self.points -= progress
