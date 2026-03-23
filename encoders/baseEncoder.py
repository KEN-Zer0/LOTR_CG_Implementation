import numpy as np
from abc import ABC, abstractmethod
import Game_Model.globals

class BaseEncoder(ABC):
    def __init__(self, game):
        self.game = game

    def createRowPlanning(self):
        row = np.zeros(Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1) ## + resources
        hand = self.game.getPlayer().getHand()
        for card in hand:
            row[card.getId() - 3] = 1
        stagedEnemies = self.game.getBoard().getStagedEnemies()
        for enemy in stagedEnemies:
            row[enemy.getId() - 3] = 1
        row[-1] = self.game.getPlayer().getResourcesBySphere('Spirit')
        return row

    def createRowPlanningFull(self):
        cardPool = self.game.getPlayer().getHeroes() + self.game.getPlayer().getCardPool() + self.game.getBoard().getCardPool()
        stateVector = [0] * (3 * 3 + 15 * 2 + 25 * 2 + 2) ## to optimize
        for card in cardPool:
            cardId = card.getId()
            if cardId < 3:
                stateVector[3 * cardId] = card.getStatus()
                stateVector[3 * cardId + 1] = card.getHitpoints()
                stateVector[3 * cardId + 2] = card.getResourcePool()
            elif cardId >= 3 and cardId < 31: # both allies and enemies here
                stateVector[2 * (cardId - 3) + 9] = card.getStatus()
                stateVector[2 * (cardId - 3) + 10] = card.getHitpoints()
            else: # lands here
                stateVector[2 * (cardId - 31) + 65] = card.getStatus() 
                stateVector[2 * (cardId - 31) + 66] = card.getPoints() 
        stateVector[-2] = self.game.getPlayer().getThreat()
        stateVector[-1] = self.game.getBoard().getQuestDeck().getTotalProgress()
        return stateVector


    @abstractmethod
    def createRowQuesting(self):
        pass

    def createRowDefense(self):
        cardsAvailable = self.game.getPlayer().getUntappedCharacters()
        engagedEnemies = self.game.getBoard().getEnemiesEngaged() 
        row = np.zeros(3 + Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1) ## heroes + allies + enemies overall + round
        for card in cardsAvailable:
            row[card.getId()] = 1
        for enemy in engagedEnemies:
            row[enemy.getId()] = 1
        row[-1] = self.game.getTurnNumber()
        return row

    def encodePlanning(self, type): ## actor, critic, macro
        if type == 'critic' or type == 'macro':
            return self.createRowPlanning()
        else:
            cardsAvailable = self.filterCards()
            if not cardsAvailable:
                return []
            resourcesAvailable = self.game.getPlayer().getResourcesBySphere('Spirit')
            stagedEnemies = self.game.getBoard().getStagedEnemies()
            state = np.zeros((len(cardsAvailable), Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1)) ## + resources
            for row in range(len(cardsAvailable)):
                if stagedEnemies:
                    for enemy in stagedEnemies:
                        state[row][enemy.getId() - 3] = 1
                state[row][cardsAvailable[row] - 3] = 1
                state[row][-1] = resourcesAvailable
            return state

    def encodeQuesting(self, type): ## +args
        if type == 'critic' or type == 'macro':
            return self.createRowQuesting()
        else:
            row = self.createRowQuesting()
            cardsAvailable = self.game.getPlayer().getAllCharacters()
            state = np.repeat(row[np.newaxis, :], len(cardsAvailable), 0)
            for i in range(len(cardsAvailable)):
                for card in cardsAvailable:
                    if cardsAvailable[i].getId() == card.getId():
                        continue
                    state[i][card.getId()] = 0
            return state

    def encodeDefense(self, type):
        if type == 'critic' or type == 'macro':
            return self.createRowDefense()
        else:
            row = self.createRowDefense()
            cardsAvailable = self.game.getPlayer().getUntappedCharacters()
            state = np.repeat(row[np.newaxis, :], len(cardsAvailable), 0)
            for i in range(len(cardsAvailable)):
                for card in cardsAvailable:
                    if cardsAvailable[i].getId() == card.getId():
                        continue
                    state[i][card.getId()] = 0
            return state

    def filterCards(self):
        hand = self.game.getPlayer().getHand()
        if not len(hand):
            return []
        cardsAvailable = []
        resourcesAvailable = self.game.getPlayer().getResourcesBySphere('Spirit')
        for card in hand:
            if card.getCost() <= resourcesAvailable:
                cardsAvailable.append(card.getId())
        return cardsAvailable
