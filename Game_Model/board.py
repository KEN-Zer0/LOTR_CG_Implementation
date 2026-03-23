from Game_Model.land import Land
from Game_Model.enemy import Enemy
import Game_Model.globals
from mainConfig import difficulty

class Board:
    def __init__(self, questDeck, encounterDeck):
        self.questDeck = questDeck
        self.encounterDeck = encounterDeck
        self.stagingArea = []
        self.engagementArea = []
        self.activeLand = None
        self.graveyard = []
        self.combinedThreat = 0
        self.shuffleEncounterDeck()

    def getQuestDeck(self):
        return self.questDeck

    def getEncounterDeck(self):
        return self.encounterDeck.getCardList()

    def getAllNamesOfEncounterDeck(self):
        cardList = self.getEncounterDeck()
        if not cardList:
            return
        names = [cardList[0].getName()]
        i = 1
        while i < len(cardList):
            name = cardList[i].getName()
            i += 1
            if names.count(name) > 0:
                continue
            names.append(name)
        return names

    def getStagingArea(self):
        return self.stagingArea

    def setStagingArea(self, stagingArea):
        self.stagingArea = stagingArea

    def getEnemiesEngaged(self):
        return self.engagementArea

    def setEnemiesEngaged(self, enemiesEngaged):
        self.engagementArea = enemiesEngaged

    def getGraveyard(self):
        return self.graveyard

    def getCardPool(self):
        cardPool = self.encounterDeck.cardList + self.stagingArea + self.engagementArea + self.graveyard
        if self.activeLand:
            cardPool.append(self.activeLand)
        return cardPool

    def getStagedEnemies(self):
        enemies = []
        for card in self.stagingArea:
            if isinstance(card, Enemy):
                enemies.append(card)
        return enemies

    def getActiveLand(self):
        return self.activeLand

    def setActiveLand(self, activeLand):
        self.activeLand = activeLand

    def getAllLands(self):
        lands = []
        for card in self.stagingArea:
            if isinstance(card, Land):
                lands.append(card)
        return lands

    def getCombinedThreat(self):
        return self.combinedThreat

    # def setCombinedThreat(self):
    #     if not self.stagingArea:
    #         return
    #     for card in self.stagingArea:
    #         self.combinedThreat += card.getThreat()

    def findCardOnTable(self, cardId):
        if not self.stagingArea:
            return None
        for card in self.stagingArea:
            if card.getId() == cardId:
                return card
        return None

    def shuffleEncounterDeck(self):
        self.encounterDeck.shuffle()

    def revealCard(self):
        return self.encounterDeck.takeOffTop()

    def addCard(self, card):
        card.setStatus(1)
        self.stagingArea.append(card)
        self.combinedThreat += card.getThreat()

    def scenarioSetup(self):
        if difficulty == 'hard':
            forestSpider = self.encounterDeck.findCard('Forest Spider')
            self.addCard(forestSpider)
            self.encounterDeck.removeCard(forestSpider)
            oldForestRoad = self.encounterDeck.findCard('Old Forest Road')
            self.addCard(oldForestRoad)
            self.encounterDeck.removeCard(oldForestRoad)
        self.shuffleEncounterDeck()

    def addToStagingArea(self): 
        card = self.revealCard()
        if not card:
            # print('out of cards in the encounter deck')
            return
        self.addCard(card)

    def removeFromStagingArea(self, card):
        self.combinedThreat -= card.getThreat()
        self.stagingArea.remove(card)

    def dealProgress(self, progress):
        if self.activeLand:
            self.activeLand.placeProgressTokens(progress)
            if self.activeLand.getPoints() <= 0:
                self.questDeck.dealProgress(abs(self.activeLand.getPoints()))
                self.graveyard.append(self.activeLand)
                self.activeLand.setStatus(3)
                self.activeLand.setPoints(0)
                self.activeLand = None
        else:
            self.questDeck.dealProgress(progress)

    def travelToLocation(self, card):
        card.setStatus(2)
        self.activeLand = card
        self.removeFromStagingArea(card)

    def doEngagementChecks(self, threat):
        enemies = self.getStagedEnemies()
        if not enemies:
            return
        for enemy in enemies:
            if enemy.engagement <= threat:
                self.addToEngagementArea(enemy)

    def addToEngagementArea(self, card):
        self.removeFromStagingArea(card)
        card.setStatus(2)
        self.engagementArea.append(card)

    def removeFromEngagementArea(self, card):
        self.engagementArea.remove(card)
        card.setStatus(3)
        self.graveyard.append(card)

    def clearDeads(self):
        for enemy in self.engagementArea:
            if enemy.isDead():
                self.removeFromEngagementArea(enemy)

    def endTurn(self):
        self.clearDeads()

    def reset(self):
        self.questDeck.resetQuest()
        self.encounterDeck.cardList += self.stagingArea
        self.encounterDeck.cardList += self.engagementArea
        if self.activeLand:
            self.encounterDeck.cardList.append(self.activeLand)
        self.encounterDeck.cardList += self.graveyard
        for card in self.encounterDeck.cardList:
            card.setStatus(0)
            if isinstance(card, Enemy):
                card.restoreDefaultHitpoints()
            else:
                card.restoreDefaultPoints()
        self.combinedThreat = 0
        self.stagingArea = []
        self.engagementArea = []
        self.activeLand = None
        self.graveyard = []

    def hardReset(self):
        self.reset() ### to remove?????????????
        Game_Model.globals.decks['Quest Deck'] = self.questDeck
        Game_Model.globals.decks['Encounter Deck'] = self.encounterDeck
