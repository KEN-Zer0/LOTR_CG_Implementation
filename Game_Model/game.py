import random

class Game():
    def __init__(self, board, player):
        self.board = board
        self.player = player
        self.turn = 0
        self.turnsWithoutDecision = [0, 0, 0, 0, 0] # planning, questing, travel, defense, attack

    def getBoard(self):
        return self.board

    def getPlayer(self):
        return self.player

    def getTurnNumber(self):
        return self.turn

    def copy(self):
        newGame = Game(self.board, self.player)
        newGame.turn = self.turn
        return newGame

    def applyCard(self, name):
        card = self.board.encounterDeck.findCard(name)
        self.board.addCard(card)
        self.board.encounterDeck.getCardList().remove(card)

    def setupGame(self):
        self.board.scenarioSetup()
        self.player.shufflePlayerDeck()
        self.player.drawHand()

    def resourcePhase(self):
        self.player.readyTurn()

    def randomPlanning(self):
        playerHand = self.player.getHand()
        if not playerHand:
            self.turnsWithoutDecision[0] += 1
            return
        slen = random.randint(0, len(playerHand))
        for _ in range(slen):
            card = random.choice(playerHand)
            if self.player.getResourcesBySphere(card.sphere) >= card.cost:
                self.player.spendResourcesBySphere(card.sphere, card.cost)
                self.player.addToAllies(card)

    def expertPlanning(self):
        gandalf = self.player.findCardInHandByName('Gandalf')
        if gandalf:
            if self.player.getResourcesBySphere('Neutral') >= 5:
                self.player.spendResourcesBySphere(gandalf.sphere, gandalf.cost)
                self.player.addToAllies(gandalf)
                return
            if self.player.getResourcesBySphere('Spirit') > 3:
                self.player.findAndSpend('Wandering Took')
                return
        else:
            self.randomPlanning()

    def planningPhase(self, cardId):
        return self.player.setCardForPlanning(cardId)

    def macroPlanning(self, action):
        budget = self.player.getResourcesBySphere('Spirit')
        playerHand = self.player.getHand()
        if action == 0: ## buy cheap
            playerHand.sort(key=lambda x: 1 / x.cost, reverse=True)
        elif action == 1: ## buy the best willpower
            playerHand.sort(key=lambda x: x.willpower / x.cost, reverse=True)
        elif action == 2:
            playerHand.sort(key=lambda x: (0.8 * x.willpower + 0.2 * x.defense) / x.cost, reverse=True)
        elif action == 3:
            playerHand.sort(key=lambda x: (0.6 * x.willpower + 0.4 * x.defense) / x.cost, reverse=True)
        elif action == 4:
            playerHand.sort(key=lambda x: (0.4 * x.willpower + 0.6 * x.defense) / x.cost, reverse=True)
        elif action == 5:
            playerHand.sort(key=lambda x: (0.2 * x.willpower + 0.8 * x.defense) / x.cost, reverse=True)
        elif action == 6: ## buy the best defense
            playerHand.sort(key=lambda x: x.defense / x.cost, reverse=True)
        for card in playerHand:
            if card.cost < budget:
                self.player.spendResourcesBySphere(card.sphere, card.cost)
                self.player.addToAllies(card)
                budget -= card.cost
                if budget < 2:
                    return

    def randomQuesting(self):
        combinedWillpower = 0
        playerCharacters = self.player.getAllCharacters()
        if not playerCharacters:
            self.turnsWithoutDecision[1] += 1
            return
        slen = random.randint(0, len(playerCharacters))
        i = 0
        while i < slen:
            card = random.choice(playerCharacters)
            if not card.isTapped():
                combinedWillpower += card.getWillpower()
                card.tap()
                i += 1
            if self.player.checkIfAllTapped():
                break
        self.resolveQuesting(combinedWillpower)

    def expertQuesting(self):
        threatLevel = self.board.getCombinedThreat()
        playerCharacters = self.player.getAllCharacters()
        playerCharacters.sort(key=lambda x: x.willpower / x.defense if x.defense else 0, reverse=True)
        combinedWillpower = 0
        if not playerCharacters:
            return
        for card in playerCharacters:
            if combinedWillpower < threatLevel + 2:
                combinedWillpower += card.getWillpower()
                card.tap() ### + set status???
        self.resolveQuesting(combinedWillpower)

    def questingPhase(self, cardList):
        return self.player.setCardsForQuesting(cardList)
        
    def resolveQuesting(self, combinedWillpower):
        self.board.addToStagingArea()
        result = combinedWillpower - self.board.getCombinedThreat()
        if result > 0:
            self.board.dealProgress(result)
            return
        self.player.increaseThreat(abs(result))

    def macroQuesting(self, action):
        threatLevel = self.board.getCombinedThreat()
        playerCharacters = self.player.getAllCharacters()
        combinedWillpower = 0
        if action == 0: ### play all-in
            for card in playerCharacters:
                combinedWillpower += card.getWillpower()
                card.tap() ### + set status???
        elif action == 1: ### play the strongest up to threshold
            playerCharacters.sort(key=lambda x: x.willpower, reverse=True)
            self.setCardsUpToThreatLevel(playerCharacters, threatLevel)
        elif action == 2:
            playerCharacters.sort(key=lambda x: 0.8 * x.willpower + 0.2 * x.defense, reverse=True)
            self.setCardsUpToThreatLevel(playerCharacters, threatLevel)
        elif action == 3:
            playerCharacters.sort(key=lambda x: 0.6 * x.willpower + 0.4 * x.defense, reverse=True)
            self.setCardsUpToThreatLevel(playerCharacters, threatLevel)
        elif action == 4:
            playerCharacters.sort(key=lambda x: 0.4 * x.willpower + 0.6 * x.defense, reverse=True)
            self.setCardsUpToThreatLevel(playerCharacters, threatLevel)
        elif action == 5:
            playerCharacters.sort(key=lambda x: 0.2 * x.willpower + 0.8 * x.defense, reverse=True)
            self.setCardsUpToThreatLevel(playerCharacters, threatLevel)
        elif action == 6: ## play with the lowest defense
            playerCharacters.sort(key=lambda x: x.defense)
            for card in playerCharacters:
                if combinedWillpower < threatLevel:
                    combinedWillpower += card.getWillpower()
                    card.tap() ### + set status???
        self.resolveQuesting(combinedWillpower)

    def setCardsUpToThreatLevel(self, cardList, threatLevel):
        combinedWillpower = 0
        for card in cardList:
            if combinedWillpower < threatLevel:
                combinedWillpower += card.getWillpower()
                card.tap() ### + set status???
        return combinedWillpower

    def randomTravelPhase(self):
        activeLand = self.board.getActiveLand()
        if activeLand:
            self.turnsWithoutDecision[2] += 1
            return
        lands = self.board.getAllLands()
        if not lands:
            self.turnsWithoutDecision[2] += 1
            return
        lands.append(None)
        land = random.choice(lands)
        if not land: return
        self.board.travelToLocation(land)

    def expertTravelPhase(self): # to optimize!!!!!!!!!!!!!! - points to threat ratio should exceed kind of threshold????
        # print('Travel Phase')
        activeLand = self.board.getActiveLand()
        if activeLand:
            return
        lands = self.board.getAllLands()
        if not lands:
            return
        lands.sort(key=lambda x: x.points / x.threat) # threat can be zero????
        self.board.travelToLocation(lands[0])

    def randomDefense(self):
        enemiesEngaged = self.board.getEnemiesEngaged()
        if not enemiesEngaged:
            return
        untapped = self.player.getUntappedCharacters()
        if not untapped:
            self.turnsWithoutDecision[3] += 1
        for enemy in enemiesEngaged:
            defender = self.player.declareRandomDefender()
            if defender:
                result = defender.defense - enemy.attack
                if result < 0:
                    defender.takeDamage(abs(result))
            else:
                self.player.randomUndefended(enemy.attack)

    def macroDefense(self, action):
        playerCharacters = self.player.getUntappedCharacters()
        enemiesEngaged = self.board.getEnemiesEngaged()
        defenders = []
        dlen = min(len(playerCharacters), len(enemiesEngaged))
        if action == 0: # play the strongest in defense
            playerCharacters.sort(key=lambda x: x.defense + x.hitpoints, reverse=True)
            for i in range(dlen):
                defenders.append(playerCharacters[i])
        elif action == 1: # play the strongest without full enemy coverage or play without defense
            playerCharacters.sort(key=lambda x: x.defense + x.hitpoints, reverse=True) # sort from the highest
            if dlen > 1:
                for i in range(dlen - 1):
                    defenders.append(playerCharacters[i])
        elif action == 2: # play with saving cards for questing
            playerCharacters.sort(key=lambda x: x.willpower, reverse=False) # sort from the lowest
            for i in range(dlen):
                defenders.append(playerCharacters[i])
        elif action == 3: # play without defense
            pass
        self.resolveDefense(defenders)

    def resolveDefense(self, defenders):
        enemiesEngaged = self.board.getEnemiesEngaged()
        enemiesEngaged.sort(key=lambda x: x.attack, reverse=True) # sort from the strongest enemies
        for enemy in enemiesEngaged:
            if not defenders:
                self.player.randomUndefended(enemy.attack)
                continue
            defender = defenders.pop(0)
            defender.tap() # + set status?
            result = defender.defense - enemy.attack
            if result < 0:
                defender.takeDamage(abs(result))

    def expertDefense(self): # to optimise!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!11
        # print('Expert Defense Phase:')
        enemiesEngaged = self.board.getEnemiesEngaged() 
        if not enemiesEngaged:
            return
        enemiesEngaged.sort(key=lambda x: x.attack, reverse=True)
        untapped = self.player.getUntappedCharacters()
        if untapped:
            untapped.sort(key=lambda x: x.defense, reverse=True)
        for enemy in enemiesEngaged:
            if not untapped:
                self.player.expertUndefended(enemy.getAttack())
                continue
            defender = untapped[0] ## take character with the highest defense
            result = defender.defense - enemy.attack
            if result < 0:
                defender.takeDamage(abs(result))
            defender.tap()
            untapped.remove(defender)

    # @staticmethod
    # def expertDefender(enemy, untapped): ################ take ally as defender at first
    #     defender = None
    #     for card in untapped:
    #         if isinstance(card, Ally):
    #             defender = card
    #             return defender
    #     defender = random.choice(untapped)
    #     return defender

    def randomAttack(self):
        enemiesEngaged = self.board.getEnemiesEngaged()
        untappedCharacters = self.player.getUntappedCharacters()
        if not untappedCharacters or not enemiesEngaged:
            self.turnsWithoutDecision[4] += 1
            return
        slen = random.randint(0, len(untappedCharacters))
        if not slen:
            return
        playerCharacters = random.sample(untappedCharacters, k=slen)
        for character in playerCharacters:
            randomTarget = random.choice(enemiesEngaged)
            result = randomTarget.defense - character.attack
            if result < 0:
                randomTarget.takeDamage(abs(result))
                if randomTarget.isDead():
                    self.board.removeFromEngagementArea(randomTarget)
            if not enemiesEngaged:
                return

    def expertAttack(self): # to optimise!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!11 - attack one enemy until it's dead
        # print('Expert Attack Phase:')
        untapped = self.player.getUntappedCharacters()
        if not untapped:
            return  
        untapped.sort(key=lambda x: x.attack, reverse=True)
        enemiesEngaged = self.board.getEnemiesEngaged() 
        if not enemiesEngaged:
            return
        enemiesEngaged.sort(key=lambda x: x.defense + x.hitpoints)
        for enemy in enemiesEngaged:
            if not untapped:
                return
            attacker = untapped[0] # take character with max attack
            result = enemy.defense - attacker.attack
            if result < 0:
                enemy.takeDamage(abs(result))
            if enemy.isDead():
                self.board.removeFromEngagementArea(enemy)
            if not enemiesEngaged:
                return
            attacker.tap()
            untapped.remove(attacker)

    def encounterPhase(self):
        # print('Encounter Phase')
        threat = self.player.getThreat()
        self.board.doEngagementChecks(threat)

    def getDecisionProbs(self):
        probs = []
        for dNum in self.turnsWithoutDecision:
            prob = (self.turn - dNum) / self.turn * 100
            probs.append(round(prob, 2))
        return probs

    def typeOfLoss(self, episodesFailHeroes, episodesFailThreat):
        if not self.player.getHeroes():
            episodesFailHeroes.append(self.turn)
            return
        if self.player.getThreat() >= 50:
            episodesFailThreat.append(self.turn)
            return
        print('smth went wrong')

    def refreshPhase(self):
        self.board.endTurn()
        self.player.endTurn()
        self.turn += 1

    def reset(self):
        self.board.reset()
        self.player.reset()
        self.turn = 0
        self.turnsWithoutDecision = [0, 0, 0, 0, 0]
