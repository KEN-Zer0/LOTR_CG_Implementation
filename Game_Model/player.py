from Game_Model.game import Game
import random
import Game_Model.globals
from Game_Model.hero import Hero

class Player:
    def __init__(self, playerDeck, heroes, threat):
        self.playerDeck = playerDeck
        self.heroes = heroes
        self.hand = []
        self.allies = []
        self.graveyard = []
        self.threat = threat
        self.shufflePlayerDeck()

    def getPlayerDeck(self):
        return self.playerDeck.getCardList()

    def getHand(self):
        return self.hand

    def setHandAndAllies(self, hand, allies):
        self.hand = hand
        self.allies = allies

    def findCardInHandById(self, cardId): # if hand is empty condition to add
        if not self.hand:
            return None
        for card in self.hand:
            if card.getId() == cardId:
                return card
        return None

    def findCardInHandByName(self, name):
        if not self.hand:
            return None
        for card in self.hand:
            if card.getName() == name:
                return card
        return None

    # def findGandalfInHand(self):
    #     if not self.hand:
    #         return None
    #     for card in self.hand:
    #         cardId = card.getId()
    #         if cardId == 15 or cardId == 16 or cardId == 17:
    #             return card
    #     return None

    def findCardOnTable(self, cardId): # if table is empty condition to add
        allCharacters = self.heroes + self.allies
        for card in allCharacters:
            if card.getId() == cardId:
                return card
        return None
    
    ###########################################################################################################

    def findAndSpend(self, name):
        card = self.findCardInHandByName(name)
        if not card:
            return
        if self.getResourcesBySphere(card.getSphere()) >= card.getCost():
            self.spendResourcesBySphere(card.getSphere(), card.getCost())
            self.addToAllies(card)

    def findCardInPlay(self, name):
        for card in self.getAllCharacters():
            if card.getName() == name:
                return card
        return None

    def getHeroes(self):
        return self.heroes

    def getAllies(self):
        return self.allies

    def getAllCharacters(self):
        return self.heroes + self.allies

    def getCharactersBySphere(self, sphere):
        characters = self.getAllCharacters()
        bySphere = []
        for character in characters:
            if character.getSphere() == sphere:
                bySphere.append(character)
        return bySphere

    def getGraveyard(self):
        return self.graveyard

    def getCardPool(self):
        return self.playerDeck.cardList + self.hand + self.allies + self.graveyard

    def getUntappedCharacters(self):
        characters = self.getAllCharacters()
        untappedCharacters = []
        for character in characters:
            if not character.isTapped():
                untappedCharacters.append(character)
        return untappedCharacters

    def getThreat(self):
        return self.threat

    def draw(self):
        if self.playerDeck.size() > 0:
            card = self.playerDeck.takeOffTop()
            card.setStatus(1)
            self.hand.append(card)

    def readyTurn(self):
        for hero in self.heroes:
            hero.addResourceToken()
        self.draw()

    def shufflePlayerDeck(self):
        self.playerDeck.shuffle()

    def drawHand(self):
        for _ in range(0, 7):
            self.draw()

    def getResourcesBySphere(self, sphere):
        total = 0
        for hero in self.heroes:
            if hero.sphere == sphere or sphere == 'Neutral':
                total += hero.getResourcePool()
        return total

    def spendResourcesBySphere(self, sphere, cost):
        tokensLeft = cost
        for hero in self.heroes:
            if tokensLeft and hero.sphere == sphere or sphere == 'Neutral':
                tokensLeft = hero.spendResourceTokens(tokensLeft)

    def addToAllies(self, card):
        card.setStatus(2)
        self.allies.append(card)
        self.hand.remove(card)

    def increaseThreat(self, threat):
        self.threat += threat
        if not Game_Model.globals.gameWin and self.threat >= 50 or not self.heroes:
            Game_Model.globals.gameOver = True

    def checkIfAllTapped(self):
        characters = self.heroes + self.allies
        for character in characters:
            if not character.isTapped():
                return False
        return True

    def untapAll(self):
        for hero in self.heroes:
            hero.setStatus(0)
            hero.untap()
        for ally in self.allies:
            ally.setStatus(2)
            ally.untap()

    def declareRandomDefender(self):
        untappedCharacters = self.getUntappedCharacters()
        if untappedCharacters:
            defender = random.choice(untappedCharacters)
            defender.tap()
            return defender
        else:
            return None

    def randomUndefended(self, attack):
        if self.heroes:
            randomHero = random.choice(self.heroes)
            randomHero.takeDamage(attack)
            if randomHero.isDead():
                randomHero.setStatus(3)
                self.graveyard.append(randomHero)
                self.heroes.remove(randomHero)
        else:
            if not Game_Model.globals.gameWin:
                Game_Model.globals.gameOver = True

    def expertUndefended(self, attack):
        if self.heroes:
            self.heroes.sort(key=lambda x: x.hitpoints, reverse=True)
            target = self.heroes[0]
            target.takeDamage(attack)
            if target.isDead():
                target.setStatus(3)
                self.graveyard.append(target)
                self.heroes.remove(target)
        else:
            if not Game_Model.globals.gameWin:
                Game_Model.globals.gameOver = True

    def setCardForPlanning(self, cardId):
        if not self.hand:
            return False
        card = self.findCardInHandById(cardId)
        if not card:
            return False
        if card.getCost() > self.getResourcesBySphere(card.getSphere()):
            return False
        self.spendResourcesBySphere(card.getSphere(), card.getCost())
        self.addToAllies(card)
        return True

    def setCardsForQuesting(self, cardList):
        if not cardList:
            return 0
        combinedWillpower = 0
        for card in cardList:
            if isinstance(card, Hero):
                card.setStatus(1)
            else:
                card.setStatus(3)
            combinedWillpower += card.getWillpower()
            card.tap()
        return combinedWillpower

    def setCardsForCombat(self, cardIdList):
        cards = []
        for cardId in cardIdList:
            card = self.findCardOnTable(cardId)
            if not card:
                return
            if card.isTapped():
                return
            if isinstance(card, Hero):
                card.setStatus(2)
            else:
                card.setStatus(4)
            card.tap()
            cards.append(card)
        return cards

    def clearDeads(self):
        for hero in self.heroes:
            if hero.isDead():
                hero.setStatus(3)
                self.graveyard.append(hero)
                self.heroes.remove(hero)
        for ally in self.allies:
            if ally.isDead() or ally.getSphere() == 'Neutral':
                ally.setStatus(5)
                self.graveyard.append(ally)
                self.allies.remove(ally)

    def endTurn(self):
        self.increaseThreat(1)
        self.clearDeads()
        self.untapAll()

    def reset(self):
        self.playerDeck.cardList += self.hand
        self.playerDeck.cardList += self.allies
        for card in self.graveyard:
            if isinstance(card, Hero):
                self.heroes.append(card)
            else:
                self.playerDeck.cardList.append(card)
        for hero in self.heroes:
            hero.untap()
            hero.setStatus(0)
            hero.setResourcePool(0)
            hero.restoreDefaultHitpoints()
        for card in self.playerDeck.cardList:
            card.untap()
            card.setStatus(0)
            card.restoreDefaultHitpoints()
        self.hand = []
        self.allies = []
        self.graveyard = []
        self.threat = 24 # watch out !!!!!!!!!!!!!!!

    def hardReset(self):
        self.reset() ###### to remove??????????????
        Game_Model.globals.heroes = self.heroes
        Game_Model.globals.decks['Player Deck'] = self.playerDeck
