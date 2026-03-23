from abc import ABC, abstractmethod
from numpy.lib.histograms import _histogram_bin_edges_dispatcher
from Game_Model.board import Board
from Game_Model.player import Player
from Game_Model.game import Game
import Game_Model.globals
import numpy as np
from encoders.questingEncoders import EnemiesRound, EnemiesLandsRound, EnemiesCombinedThreat, CombinedThreatEngaged

class BaseEnv(ABC):
    def __init__(self, encoderType):
        player = Player(Game_Model.globals.decks['Player Deck'], Game_Model.globals.heroes, 24) ## threat level should be in globals!!!!!!!!!!!!!!!
        board = Board(Game_Model.globals.decks['Quest Deck'], Game_Model.globals.decks['Encounter Deck'])
        self.game = Game(board, player)
        self.game.setupGame()
        self.game.resourcePhase()
        self.encoder = None
        self.setEncoder(encoderType)
        # self.cardsAvailable = []
        # self.planning_action = None
        # self.handIds = []

    def setEncoder(self, encoderType):
        if encoderType == 0:
            self.encoder = EnemiesRound(self.game)
        elif encoderType == 1:
            self.encoder = EnemiesLandsRound(self.game)
        elif encoderType == 2:
            self.encoder = EnemiesCombinedThreat(self.game)
        else:
            self.encoder = CombinedThreatEngaged(self.game)

    # @abstractmethod
    # def featuresPlanningActor(self):
    #     pass

    # @abstractmethod
    # def featuresPlanningCritic(self):
    #     pass

    # @abstractmethod
    # def featuresQuestingActor(self):
    #     pass

    # @abstractmethod
    # def featuresQuestingCritic(self):
    #     pass

    @abstractmethod
    def step_planning(self, action):
        pass

    @abstractmethod
    def step_questing(self, action):
        pass

    @abstractmethod
    def step_defense(self, action):
        pass

    def travelPhase(self, mode):
        if mode[2] == 'e':
            self.game.expertTravelPhase()
        else:
            self.game.randomTravelPhase()
        self.game.encounterPhase()

    def endRound(self, mode):
        if mode[4] == 'e':
            self.game.expertAttack()
        else:
            self.game.randomAttack()
        self.game.refreshPhase()
        self.game.resourcePhase()

    def reset(self):
        self.game.reset()
        self.game.setupGame()
        self.game.resourcePhase()
        Game_Model.globals.gameWin = False
        Game_Model.globals.gameOver = False

    def hardReset(self):
        self.game.getBoard().hardReset()
        self.game.getPlayer().hardReset()
