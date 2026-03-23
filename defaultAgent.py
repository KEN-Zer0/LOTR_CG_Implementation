from Game_Model.board import Board
from Game_Model.player import Player
from Game_Model.game import Game
import Game_Model.globals
import numpy as np

class DefaultAgent:
    def __init__(self, mode, num_episodes):
        self.mode = mode
        self.num_episodes = num_episodes
        player = Player(Game_Model.globals.decks['Player Deck'], Game_Model.globals.heroes, 24)
        board = Board(Game_Model.globals.decks['Quest Deck'], Game_Model.globals.decks['Encounter Deck'])
        self.game = Game(board, player)
        self.game.setupGame()
        self.episodeProbs = []
        self.episodesSuccess = []
        self.episodesFailHeroes = []
        self.episodesFailThreat = []

    def planningPhase(self):
        if self.mode[0] == 'r':
            self.game.randomPlanning()
        elif self.mode[0] == 'e':
            self.game.expertPlanning()
        else:
            print(f'planning phase type not recognized')

    def questingPhase(self):
        if self.mode[0] == 'r':
            self.game.randomQuesting()
        elif self.mode[0] == 'e':
            self.game.expertQuesting()
        else:
            print(f'questing phase type not recognized')

    def travelPhase(self):
        if self.mode[0] == 'r':
            self.game.randomTravelPhase()
        elif self.mode[0] == 'e':
            self.game.expertTravelPhase()
        else:
            print(f'travel phase type not recognized')

    def defensePhase(self):
        if self.mode[0] == 'r':
            self.game.randomDefense()
        elif self.mode[0] == 'e':
            self.game.expertDefense()
        else:
            print(f'defense phase type not recognized')

    def attackPhase(self):
        if self.mode[0] == 'r':
            self.game.randomAttack()
        elif self.mode[0] == 'e':
            self.game.expertAttack()
        else:
            print(f'attack phase type not recognized')

    def reset(self):
        self.game.reset()
        self.game.setupGame()
        Game_Model.globals.gameWin = False
        Game_Model.globals.gameOver = False

    def hardReset(self):
        self.game.getBoard().hardReset()
        self.game.getPlayer().hardReset()

    def simulate(self):
        score_history = []
        for _ in range(self.num_episodes):
            while 1:
                if Game_Model.globals.gameWin:
                    score_history.append(1)
                    self.episodesSuccess.append(self.game.getTurnNumber())
                    break
                if Game_Model.globals.gameOver:
                    score_history.append(0)
                    self.game.typeOfLoss(self.episodesFailHeroes, self.episodesFailThreat)
                    break
                self.game.resourcePhase()
                self.planningPhase()
                self.questingPhase()
                self.travelPhase()
                self.game.encounterPhase()
                self.defensePhase()
                self.attackPhase()
                self.game.refreshPhase()
            probs = self.game.getDecisionProbs()
            self.episodeProbs.append(probs)
            self.reset()
        self.hardReset()
        return score_history

    def getDecisionProbs(self):
        return np.mean(self.episodeProbs, axis=0)

    def getEpisodeLengths(self):
        return self.episodesSuccess, self.episodesFailHeroes, self.episodesFailThreat





