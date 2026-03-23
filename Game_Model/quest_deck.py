from Game_Model.deck import Deck
import Game_Model.globals

class QuestDeck(Deck):
    def __init__(self, name):
        super(QuestDeck, self).__init__(name)
        self.totalProgress = 0

    def copy(self):
        newQuestDeck = QuestDeck(self.name)
        newQuestDeck.cardList = self.cardList
        return newQuestDeck

    def getTotalProgress(self):
        return self.totalProgress

    def resetQuest(self):
        self.cardList[0].restoreDefaultPoints()
        self.totalProgress = 0

    def dealProgress(self, progress):
        self.totalProgress += progress
        card = self.cardList[0]
        card.placeProgressTokens(progress)
        if not Game_Model.globals.fullGame and card.getPoints() <= 0:
            Game_Model.globals.gameWin = True
            return
        if card.getPoints() <= 0:
            self.takeOffTop() 
        if len(self.cardList) == 0:
            Game_Model.globals.gameWin = True

    def getCurrentQuest(self):
        return self.cardList[0]

    def setLastQuest(self, points):
        quest = self.cardList[-1]
        quest.setPoints(points)
