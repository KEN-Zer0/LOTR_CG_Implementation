import numpy as np
import Game_Model.globals
from envs.baseEnv import BaseEnv

class LowLevelEnv(BaseEnv):
    def __init__(self, encoderType):
        super(LowLevelEnv, self).__init__(encoderType)
        self.cardsAvailable = []
        self.planning_action = None
        self.handIds = []

    def step_planning(self, action):
        self.cardsAvailable = self.encoder.filterCards()
        cardId = self.cardsAvailable[action]
        if not self.game.planningPhase(cardId):
            print('smth went wrong at planning')
        for i in range(len(self.handIds)):
            if self.handIds[i] == self.cardsAvailable[action]:
                idx = i
        self.planning_action[idx] = 1
        return

    def step_questing(self, action): ## remove game condition check????
        if len(action) == 1:
            action = np.squeeze(action, axis=0)
        else:
            action = np.squeeze(action)
        cardsAvailable = self.game.getPlayer().getAllCharacters()
        cardList = []
        for i in range(len(action)):
            if action[i]:
                cardList.append(cardsAvailable[i])
        if not cardList:
            return self.encoder.encodeQuesting('critic'), -1, True
        combinedWillpower = self.game.getPlayer().setCardsForQuesting(cardList)
        self.game.resolveQuesting(combinedWillpower)
        # if Game_Model.globals.gameWin:
        #     return self.encoder.encodeQuesting('critic'), 1, True
        # if Game_Model.globals.gameOver:
        #     return self.encoder.encodeQuesting('critic'), -1, True
        return self.encoder.encodeQuesting('critic'), 0, False

    def step_defense(self, action):
        if len(action) == 1:
            action = np.squeeze(action, axis=0)
        else:
            action = np.squeeze(action)
        cardsAvailable = self.game.getPlayer().getUntappedCharacters()
        cardList = []
        for i in range(len(action)):
            if action[i]:
                cardList.append(cardsAvailable[i])
        if not cardList:
            return self.encoder.encodeDefense('critic'), -1, True
        self.game.resolveDefense(cardList)
        # if Game_Model.globals.gameWin:
        #     return self.encoder.encodeQuesting('critic'), 1, True
        # if Game_Model.globals.gameOver:
        #     return self.encoder.encodeQuesting('critic'), -1, True
        return self.encoder.encodeDefense('critic'), 0, False

    def endRound(self, mode):
        super().endRound(mode)
        self.updateHand()
        self.planning_action = np.zeros(len(self.handIds))

    def updateHand(self):
        self.handIds = [] ## only resource affordable
        hand = self.game.getPlayer().getHand()
        if not len(hand):
            return []
        resourcesAvailable = self.game.getPlayer().getResourcesBySphere('Spirit')
        for card in hand:
            if card.getCost() <= resourcesAvailable:
                self.handIds.append(card.getId())

    def reset(self):
        super().reset()
        self.cardsAvailable = []
        self.updateHand()
        self.planning_action = np.zeros(len(self.handIds))
        return self.encoder.encodePlanning('critic')