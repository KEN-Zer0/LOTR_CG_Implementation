import numpy as np
import Game_Model.globals
from mainConfig import difficulty
from encoders.baseEncoder import BaseEncoder

class EnemiesRound(BaseEncoder): ## enemies + round
    def __init__(self, game):
        super(EnemiesRound, self).__init__(game)

    def createRowQuesting(self):
        cardsAvailable = self.game.getPlayer().getAllCharacters()
        stagedEnemies = self.game.getBoard().getStagedEnemies()
        row = np.zeros(3 + Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1) ## heroes + allies + enemies overall + round
        for card in cardsAvailable:
            row[card.getId()] = 1
        for enemy in stagedEnemies:
            row[enemy.getId()] = 1
        row[-1] = self.game.getTurnNumber()
        return row

class EnemiesLandsRound(BaseEncoder): ## enemies + lands + round
    def __init__(self, game):
        super(EnemiesLandsRound, self).__init__(game)

    def createRowQuesting(self):
        cardsAvailable = self.game.getPlayer().getAllCharacters()
        stagedEnemies = self.game.getBoard().getStagedEnemies()
        lands = self.game.getBoard().getAllLands()
        digits = 3 + Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1 ## heroes + allies + enemies overall + round
        if difficulty == 'hard' or difficulty == 'medium':
            digits += Game_Model.globals.numberOfLands ## + lands overall
        row = np.zeros(digits) 
        for card in cardsAvailable:
            row[card.getId()] = 1
        for enemy in stagedEnemies:
            row[enemy.getId()] = 1
        if difficulty == 'hard' or difficulty == 'medium':
            for land in lands:
                row[land.getId()] = 1
        row[-1] = self.game.getTurnNumber()
        return row

class EnemiesCombinedThreat(BaseEncoder): ## enemies + combined threat
    def __init__(self, game):
        super(EnemiesCombinedThreat, self).__init__(game)

    def createRowQuesting(self): 
        cardsAvailable = self.game.getPlayer().getAllCharacters()
        stagedEnemies = self.game.getBoard().getStagedEnemies()
        combinedThreat = self.game.getBoard().getCombinedThreat()
        digits = 3 + Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1
        row = np.zeros(digits)
        for card in cardsAvailable:
            row[card.getId()] = 1
        for enemy in stagedEnemies:
            row[enemy.getId()] = 1
        row[-1] = combinedThreat
        return row

class CombinedThreatEngaged(BaseEncoder): ## combined threat + enemies engaged
    def __init__(self, game):
        super(CombinedThreatEngaged, self).__init__(game)

    def createRowQuesting(self): 
        cardsAvailable = self.game.getPlayer().getAllCharacters()
        engagedEnemies = self.game.getBoard().getEnemiesEngaged()
        combinedThreat = self.game.getBoard().getCombinedThreat()
        digits = 3 + Game_Model.globals.numberOfAllies + Game_Model.globals.numberOfEnemies + 1
        row = np.zeros(digits)
        for card in cardsAvailable:
            row[card.getId()] = 1
        for enemy in engagedEnemies:
            row[enemy.getId()] = 1
        row[-1] = combinedThreat
        return row