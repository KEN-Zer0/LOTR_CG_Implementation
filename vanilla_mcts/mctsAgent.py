from Game_Model.player import Player
from Game_Model.board import Board
from Game_Model.game import Game
import Game_Model.globals
from vanilla_mcts.node import Node
from vanilla_mcts.mcts import MCTS
import copy
import random

class MCTSAgent:
    def __init__(self, mode, playoutBudget, playoutsPerSimulation, playoutType):
        heroes = copy.deepcopy(Game_Model.globals.heroes)
        playerDeck = copy.deepcopy(Game_Model.globals.decks['Player Deck'])
        player = Player(playerDeck, heroes, 24) ### threat level should be in globals!!!!!!!!!!!!
        questDeck = copy.deepcopy(Game_Model.globals.decks['Quest Deck'])
        encounterDeck = copy.deepcopy(Game_Model.globals.decks['Encounter Deck'])
        board = Board(questDeck, encounterDeck)
        game = Game(board, player)
        game.setupGame()
        self.rootNode = Node(game, None)
        self.mode = mode
        self.playoutBudget = playoutBudget
        self.playoutsPerSimulation = playoutsPerSimulation
        self.playoutType = playoutType
        self.turnNumber = 0

    def simulate(self):
        success = None
        fail = None
        while 1:
            # print(f'round: {self.turnNumber}')
            if self.simulatePlanning():
                # print('Planning BREAK')
                break
            if self.simulateQuesting():
                # print('Questing BREAK')
                break
            if self.simulateDefense():
                # print('Defense BREAK')
                break
            self.turnNumber += 1
        if Game_Model.globals.gameWin:
            success = self.turnNumber
            reward = 1
        if Game_Model.globals.gameOver:
            fail = self.turnNumber
            reward = 0
        Game_Model.globals.gameOver = False
        Game_Model.globals.gameWin = False
        return reward, success, fail

    def checkIfLoseWin(self):
        if Game_Model.globals.gameOver or Game_Model.globals.gameWin:
            # print('isTeminal')
            return True
        return False

    def simulateMCTS(self):
        mcts = MCTS(self.rootNode, self.playoutBudget, self.playoutsPerSimulation, self.playoutType)
        # print(f'total progress before: {self.rootNode.getGame().getBoard().getQuestDeck().getTotalProgress()}')
        # print(f'untapped cards before:')
        # for card in self.rootNode.getGame().getPlayer().getUntappedCharacters():
        #     print(card.getName())
        # print(f'combined threat: {self.rootNode.getGame().getBoard().getCombinedThreat()}')
        self.rootNode = mcts.makeDecision()
        # print(f'total progress after: {self.rootNode.getGame().getBoard().getQuestDeck().getTotalProgress()}')
        # print(f'untapped cards after:')
        # for card in self.rootNode.getGame().getPlayer().getUntappedCharacters():
        #     print(card.getName())
        # print(f'combined threat: {self.rootNode.getGame().getBoard().getCombinedThreat()}')
        ######################################################
        # if self.rootNode.getGame().getBoard().getQuestDeck().cardList[0].getPoints() <= 0:
        #     # print('WIN!!!!!!!!!!!!!!')
        #     Game_Model.globals.gameWin = True
        self.rootNode.resetFamily()
        self.rootNode.isTerminal()

    def simulatePlanning(self):
        if self.mode[0] == 'e':
            game = self.rootNode.getGame()
            game.resourcePhase()
            game.expertPlanning()
            self.rootNode = Node(game, None, 'Planning')
        elif self.mode[0] == 'r':
            game = self.rootNode.getGame()
            game.resourcePhase()
            game.randomPlanning()
            self.rootNode = Node(game, None, 'Planning')
        else:
            self.simulateMCTS()
        return self.checkIfLoseWin()

    def simulateQuesting(self):
        if self.mode[1] == 'e':
            game = self.rootNode.getGame()
            game.expertQuesting()
            self.rootNode = Node(game, None, 'Questing')
        elif self.mode[1] == 'r':
            game = self.rootNode.getGame()
            game.randomQuesting()
            self.rootNode = Node(game, None, 'Questing')
        else:
            # print(f'win/false before: {Game_Model.globals.gameWin}/{Game_Model.globals.gameOver}')
            self.simulateMCTS()
            # print(f'win/false after: {Game_Model.globals.gameWin}/{Game_Model.globals.gameOver}')
        return self.checkIfLoseWin()

    def simulateTravelPhase(self, game):
        if self.mode[2] == 'e':
            game.expertTravelPhase()
        else:
            game.randomTravelPhase()

    def simulateDefense(self):
        if self.mode[3] == 'e':
            game = self.rootNode.getGame()
            self.simulateTravelPhase(game)
            game.encounterPhase()
            game.expertDefense()
            self.simulateAttack(game)
            game.refreshPhase()
            self.rootNode = Node(game, None, 'Defense')
        elif self.mode[3] == 'r':
            game = self.rootNode.getGame()
            self.simulateTravelPhase(game)
            game.encounterPhase()
            # print(f'win/false before def: {Game_Model.globals.gameWin}/{Game_Model.globals.gameOver}')
            game.randomDefense()
            # print(f'win/false after def: {Game_Model.globals.gameWin}/{Game_Model.globals.gameOver}')
            self.simulateAttack(game)
            game.refreshPhase()
            self.rootNode = Node(game, None, 'Defense')
        else:
            self.simulateMCTS()
        return self.checkIfLoseWin()

    def simulateAttack(self, game):
        if self.mode[4] == 'e':
            game.expertAttack()
        else:
            game.randomAttack()