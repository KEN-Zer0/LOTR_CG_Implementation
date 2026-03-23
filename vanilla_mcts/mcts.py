from re import sub
from Game_Model.game import Game
from Game_Model.ally import Ally
import Game_Model.globals
from vanilla_mcts.node import Node
import random
import math
import copy
import itertools
from mainConfig import reduction_planning, reduction_questing, reduction_defense

class MCTS:
    def __init__(self, rootNode, playoutBudget, playoutsPerSimulation, playoutType):
        self.rootNode = rootNode
        self.playoutBudget = playoutBudget
        self.playoutsPerSimulation = playoutsPerSimulation
        self.playoutType = playoutType ### 0 - random, 1 - expert
        self.uctConst = 1
        self.omitStaging = False
        
    def uctFn(self, node):
        return node.getUtility() / node.getVisits() + self.uctConst * math.sqrt(2 * math.log(node.getParent().getVisits()) / node.getVisits())

    def scoreFn(self, wins, turns):
        return wins * 10 + turns

    def select(self, node, lvl):
        lvl += 1
        if not node.getChildren():
            # print('Node ' + node.getName() + ' selected')
            return node
        children = node.getChildren()
        random.shuffle(children)
        for child in children:
            if child.getVisits() == 0:
                # print('Node ' + child.getName() + ' selected')
                return child
        score = 0
        result = node
        for child in children:
            newscore = self.uctFn(child)
            if newscore > score:
                score = newscore
                result = child
        return self.select(result, lvl)

    # def expand(self, node):
    #     if self.omitStaging:
    #         self.expandQuesting(node, True)
    #         self.omitStaging = False
    #         return
    #     if not node.getStage() or node.getStage() == 'Defense':
    #         self.expandPlanning(node)
    #         return
    #     if node.getStage() == 'Planning':
    #         self.expandStaging(node)
    #         return
    #     if node.getStage() == 'Staging':
    #         self.expandQuesting(node, False)
    #         return
    #     if node.getStage() == 'Questing':
    #         self.expandDefense(node)
    #         return

##################################################

    def expand(self, node):
        if not node.getStage() or node.getStage() == 'Defense':
            self.expandPlanning(node)
            return
        if node.getStage() == 'Planning':
            self.expandQuesting(node, True)
            return
        if node.getStage() == 'Questing':
            self.expandDefense(node)
            return

##################################################

    def expandPlanning(self, node):
        game = node.getGame()
        game.resourcePhase()
        legalCards = self.findLegalsPlanning(game.getPlayer())
        for name in legalCards:
            newGame = copy.deepcopy(game) # watch out!!!!!!!!!
            if name != 'None':
                card = newGame.getPlayer().findCardInHandByName(name)
                newGame.getPlayer().spendResourcesBySphere(card.sphere, card.cost)
                newGame.getPlayer().addToAllies(card)
            newNode = Node(newGame, node, 'Planning')
            node.addChild(newNode)
            # print('Node with ' + name + ' added')

    def expandQuesting(self, node, withStaging):
        game = node.getGame()
        legalSubsets = self.findLegalsQuesting(game.getPlayer(), game.getBoard().getCombinedThreat())
        if not legalSubsets:
            newGame = copy.deepcopy(game)
            newGame.resolveQuesting(0)
            newNode = Node(newGame, node, 'Questing')
            node.addChild(newNode)
            return
        for subset in legalSubsets:
            newGame = copy.deepcopy(game)
            self.subsetQuesting(newGame, subset, withStaging)
            newNode = Node(newGame, node, 'Questing')
            node.addChild(newNode)

    def expandStaging(self, node):
        game = node.getGame()
        names = game.getBoard().getAllNamesOfEncounterDeck()
        if not names:
            newNode = Node(game.getBoard(), game.getPlayer(), node, 'Staging')
            node.addChild(newNode)
            return
        for name in names:
            newGame = copy.deepcopy(game)
            newGame.applyCard(name)
            newNode = Node(newGame, node, 'Staging')
            node.addChild(newNode)

    def expandDefense(self, node):
        game = node.getGame()
        game.randomTravelPhase()
        game.encounterPhase()
        legalSubsets = self.findLegalsDefense(game.getBoard(), game.getPlayer())
        if not legalSubsets:
            newGame = copy.deepcopy(game)
            newGame.refreshPhase()
            newNode = Node(newGame, node, 'Defense')
            node.addChild(newNode)
            return
        for subset in legalSubsets:
            newGame = copy.deepcopy(game)
            self.subsetDefense(newGame, subset)
            newGame.randomAttack() ##################### sure??
            newGame.refreshPhase()
            newNode = Node(newGame, node, 'Defense')
            node.addChild(newNode)

    def backpropagate(self, node, score):
        node.incrementVisits()
        node.incrementUtility(score)
        if node.getParent():
            self.backpropagate(node.getParent(), score)

    def simulate(self, node):
        score = 0
        game = node.getGame()
        if not node.getStage() or node.getStage() == 'Defense':
            score = self.simulateComplete(game)
        if node.getStage() == 'Planning':
            score = self.simulatePlanning(game)
        # if node.getStage() == 'Staging':
        #     self.playoutBudget -= 1
        if node.getStage() == 'Questing':
            score = self.simulateQuesting(game)
        return score
    
    def makeDecision(self):
        self.buildUpTree()
        children = self.rootNode.getChildren()
        # random.shuffle(children)
        score = 0
        decision = None
        for child in children:
            if child.getVisits() == 0:
                continue
            newscore = self.uctFn(child)
            if newscore > score:
                score = newscore
                decision = child
        return decision

    def buildUpTree(self):
        if self.rootNode.getStage() == 'Planning':
            self.omitStaging = True
        while self.playoutBudget > 0:
            leafNode = self.select(self.rootNode, 0)
            self.expand(leafNode)
            score = self.simulate(leafNode)
            self.backpropagate(leafNode, score)

    


    @staticmethod
    def getSubsetWillpower(subset):
        combinedWillpower = 0
        for card in subset:
            combinedWillpower += card.getWillpower()
        return combinedWillpower

    @staticmethod
    def subsetContains(subset, names):
        for name in subset:
            if name in names:
                return True
        return False

    ##################################################################   
    def findLegalsPlanning(self, player):
        legalCards = []
        legalCards.append('None')
        playerHand = player.getHand()
        if reduction_planning:
            gandalf = player.findCardInHandByName('Gandalf')
            if gandalf and player.getResourcesBySphere(gandalf.sphere) > 4:
                legalCards.append('Gandalf')
                return legalCards
        for card in playerHand:
            if not card.getName() in legalCards and player.getResourcesBySphere(card.sphere) >= card.cost:
                legalCards.append(card.getName())
        return legalCards

    #####################################################################

    def findLegalsQuesting(self, player, combinedThreat): # to optimise: player to mainGame.getPlayer()
        playerCharacters = player.getAllCharacters()
        legalNodes = []
        for i in range(1, len(playerCharacters)):
            for subset in itertools.combinations(playerCharacters, i):
                cardList = list(subset)
                if reduction_questing:
                    if self.getSubsetWillpower(cardList) > combinedThreat + 2:
                        legalNodes.append(self.subsetToNames(cardList))
                else:
                    legalNodes.append(self.subsetToNames(cardList))
        return legalNodes

    def findLegalsDefense(self, board, player):
        enemiesEngaged = board.getEnemiesEngaged()
        if not enemiesEngaged:
            return
        playerCharacters = player.getAllCharacters()
        legalDefenders = []
        for subset in itertools.combinations(playerCharacters, len(enemiesEngaged)):
            if reduction_defense:
                if not self.containsAllyTapped(list(subset)):
                    legalDefenders.append(self.subsetToNames(list(subset)))
            else:
                legalDefenders.append(self.subsetToNames(list(subset)))
        return legalDefenders

    # def findLegalsAttack(self): ######################## do not erase!!!!!!!!!!!!!!
    #     enemiesEngaged = self.mainGame.getBoard().getEnemiesEngaged()
    #     playerCharacters = self.mainGame.getPlayer().getUntappedCharacters()
    #     if not enemiesEngaged:
    #         globals.dmode('no enemies engaged')
    #         return
    #     if not playerCharacters:
    #         globals.dmode('no player characters available')
    #         return
    #     size = len(playerCharacters)
    #     legalAttackers = []
    #     if size > len(enemiesEngaged):
    #         size = len(enemiesEngaged)
    #         for subset in itertools.combinations(playerCharacters, size):
    #             legalAttackers.append(Node(self.subsetToNames(list(subset))))
    #     else:
    #         legalAttackers.append(Node(self.subsetToNames(playerCharacters)))
    #     return legalAttackers

    def subsetQuesting(self, game, subset, withStaging):
        if not subset:
            return
        combinedWillpower = 0
        for name in subset:
            card = game.getPlayer().findCardInPlay(name)
            combinedWillpower += card.getWillpower()
            card.tap() ## + set status????
        game.resolveQuesting(combinedWillpower)

    def subsetDefense(self, game, subset):
        if not subset:
            return
        enemiesEngaged = game.getBoard().getEnemiesEngaged()
        if not enemiesEngaged:
            return
        playerCharacters = []
        for name in subset:
            card = game.getPlayer().findCardInPlay(name)
            playerCharacters.append(card)
        for enemy in enemiesEngaged:
            defender = random.choice(playerCharacters) ### sure???
            if not defender.isTapped():
                result = defender.defense - enemy.attack
                if result < 0:
                    defender.takeDamage(abs(result))
                defender.tap()
            else:
                game.getPlayer().randomUndefended(enemy.attack)

    def simulateComplete(self, game): # to optimise: include in simulate planning, questing, defense!!!
        wins = 0
        turns = 0
        for _ in range(self.playoutsPerSimulation):
            if self.playoutBudget < 0:
                break
            self.playoutBudget -= 1
            tmpGame = copy.deepcopy(game)
            while 1:
                turns += 1
                self.doTurn(tmpGame)
                if Game_Model.globals.gameOver:
                    break
                if Game_Model.globals.gameWin:
                    wins += 1
                    break
            Game_Model.globals.gameWin = False
            Game_Model.globals.gameOver = False
        return wins

    def simulatePlanning(self, game):
        wins = 0
        turns = 0
        for _ in range(self.playoutsPerSimulation):
            if self.playoutBudget < 0:
                break
            self.playoutBudget -= 1
            tmpGame = copy.deepcopy(game)
            if self.playoutType == 0:
                tmpGame.randomQuesting()
                tmpGame.randomTravelPhase()
            else:
                tmpGame.expertQuesting()
                tmpGame.expertTravelPhase()
            tmpGame.encounterPhase()
            if self.playoutType == 0:
                tmpGame.randomDefense()
                tmpGame.randomAttack()
            else:
                tmpGame.expertDefense()
                tmpGame.expertAttack()
            tmpGame.refreshPhase()
            while 1:
                turns += 1
                if Game_Model.globals.gameOver:
                    break
                if Game_Model.globals.gameWin:
                    wins += 1
                    break
                self.doTurn(tmpGame)
            Game_Model.globals.gameWin = False
            Game_Model.globals.gameOver = False
        return wins

    def simulateQuesting(self, game):
        wins = 0
        turns = 0
        for _ in range(self.playoutsPerSimulation):
            if self.playoutBudget < 0:
                break
            self.playoutBudget -= 1
            tmpGame = copy.deepcopy(game)
            if self.playoutType == 0:
                tmpGame.randomTravelPhase()
            else:
                tmpGame.expertTravelPhase()
            tmpGame.encounterPhase()
            if self.playoutType == 0:
                tmpGame.randomDefense()
                tmpGame.randomAttack()
            else:
                tmpGame.expertDefense()
                tmpGame.expertAttack()
            tmpGame.refreshPhase()
            while 1:
                turns += 1
                if Game_Model.globals.gameOver:
                    break
                if Game_Model.globals.gameWin:
                    wins += 1
                    break
                self.doTurn(tmpGame)
            Game_Model.globals.gameWin = False
            Game_Model.globals.gameOver = False
        return wins

    def doTurn(self, game):
        game.resourcePhase()
        if self.playoutType == 0:
            game.randomPlanning()
            game.randomQuesting()
            game.randomTravelPhase()
        else:
            game.expertPlanning()
            game.expertQuesting()
            game.expertTravelPhase()
        game.encounterPhase()
        if self.playoutType == 0:
            game.randomDefense()
            game.randomAttack()
        else:
            game.expertDefense()
            game.expertAttack()
        game.refreshPhase()


    # def simulateDefense(self, game): ########### to remove????????????
    #     score = 0
    #     for _ in range(self.playoutsNumber):
    #         tmpGame = copy.deepcopy(game)
    #         tmpGame.playoutAttackEnemies()
    #         tmpGame.refreshPhase()
    #         while 1:
    #             if globals.gameOver:
    #                 break
    #             if globals.gameWin:
    #                 score += 1
    #                 break
    #             tmpGame.doTurn()
    #         globals.gameWin = False
    #         globals.gameOver = False
    #     return score

    # def simulateAttack(self, node): ##################### do not erase
    #     score = 0
    #     for _ in range(self.playoutsNumber):
    #         game = copy.deepcopy(self.mainGame)
    #         game.subsetAttack(node)
    #         game.refreshPhase()
    #         while 1:
    #             if globals.gameOver:
    #                 break
    #             if globals.gameWin:
    #                 score += 1
    #                 break
    #             game.doTurn()
    #         globals.gameWin = False
    #         globals.gameOver = False
    #     return score

    # def mctsPlanning(self):
    #     nodes = []
    #     legalCards = self.findLegalsPlanning()
    #     for name in legalCards:
    #         score = 0
    #         if self.mode[0] == 'm':
    #             score = self.simulatePlanning(name)
    #         nodes.append(Node([name], score))
    #     bestNode = self.select(nodes)
    #     self.mainGame.subsetPlanning(bestNode)
    #     globals.dmode('Planning phase:')
    #     globals.dmode(bestNode)

    # def mctsQuesting(self):
    #     legalNodes = self.findLegalsQuesting(self.mainGame.getPlayer(), self.mainGame.getBoard().getCombinedThreat())
    #     for node in legalNodes:
    #         score = 0
    #         if self.mode[1] == 'm':
    #             score = self.simulateQuesting(node)
    #         node.setScore(score)
    #     bestNode = self.select(legalNodes)
    #     self.mainGame.subsetQuesting(bestNode)
    #     globals.dmode('Questing Phase:')
    #     globals.dmode(bestNode)

    # def mctsDefense(self):
    #     globals.dmode('Defense Phase:')
    #     legalDefenders = self.findLegalsDefense()
    #     if not legalDefenders:
    #         return
    #     for node in legalDefenders:
    #         score = 0
    #         if self.mode[2] == 'm':
    #             score = self.simulateDefense(node)
    #         node.setScore(score)
    #     bestNode = self.select(legalDefenders)
    #     self.mainGame.subsetDefense(bestNode)
    #     globals.dmode(bestNode)

    # def mctsAttack(self):
    #     globals.dmode('Attack Phase:')
    #     legalAttackers = self.findLegalsAttack()
    #     if not legalAttackers:
    #         return
    #     for node in legalAttackers:
    #         score = 0
    #         if self.mode[3] == 'm':
    #             score = self.simulateAttack(node)
    #         node.setScore(score)
    #     bestNode = self.select(legalAttackers)
    #     globals.dmode(f'best score: {bestNode.getScore()}')
    #     self.mainGame.subsetAttack(bestNode)
    #     globals.dmode(bestNode)

    # def planningPhase(self):
    #     if self.mode[0] == 'e':
    #         self.mainGame.expertPlanning()
    #     else:
    #         self.mctsPlanning()

    # def questingPhase(self):
    #     if self.mode[1] == 'e':
    #         self.mainGame.expertQuesting()
    #     else:
    #         self.mctsQuesting()

    # def defensePhase(self):
    #     if self.mode[2] == 'e':
    #         self.mainGame.expertDefense()
    #     else:
    #         self.mctsDefense()

    # def attackPhase(self):
    #     if self.mode[3] == 'e':
    #         self.mainGame.expertAttack()
    #     else:
    #         self.mctsAttack()

    # def buildTurn(self):
    #     globals.dmode('Turn: ' + str(self.mainGame.getTurnNumber()))
    #     self.mainGame.resourcePhase()
    #     self.planningPhase()
    #     self.questingPhase()
    #     self.mainGame.randomTravelPhase()
    #     self.mainGame.encounterPhase()
    #     self.defensePhase()
    #     self.attackPhase()
    #     self.mainGame.refreshPhase()

    # def select(self, nodes):
    #     score = 0
    #     result = None
    #     for node in nodes:
    #         newscore = node.getScore()
    #         if newscore >= score:
    #             score = newscore
    #             result = node
    #     if result and result.getScore() == 0:
    #         result = random.choice(nodes)
    #     return result

    @staticmethod
    def containsAllyTapped(subset):
        for card in subset:
            if isinstance(card, Ally) and card.isTapped():
                return True
        return False

    @staticmethod
    def subsetToNames(subset):
        names = []
        for card in subset:
            names.append(card.getName())
        return names



