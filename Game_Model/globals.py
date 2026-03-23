from Game_Model.hero import Hero
from Game_Model.ally import Ally
from Game_Model.quest import Quest
from Game_Model.enemy import Enemy
from Game_Model.land import Land
from Game_Model.quest_deck import QuestDeck
from Game_Model.regular_deck import RegularDeck
from mainConfig import difficulty, fullGame

def init():
    global gameOver
    global gameWin
    gameOver = False
    gameWin = False

    global dictOfCards
    global heroes
    global decks
    dictOfCards = {}
    heroes = []
    decks = {}

    dictOfCards['Dunhere'] = Hero(0, 'Dunhere', 2, 1, 4, 1, 'Spirit', 8)
    dictOfCards['Eowyn'] = Hero(1, 'Eowyn', 1, 1, 3, 4, 'Spirit', 9)
    dictOfCards['Eleanor'] = Hero(2, 'Eleanor', 1, 2, 3, 1, 'Spirit', 7)
    
    dictOfCards['Lorien Guide'] = Ally(3, 'Lorien Guide', 1, 1, 2, 0, 'Spirit', 3) ## ids separation = 3 cards of each!!!!!!!!!!!!
    dictOfCards['Northern Tracker'] = Ally(6, 'Northern Tracker', 2, 2, 3, 1, 'Spirit', 4)
    dictOfCards['Wandering Took'] = Ally(9, 'Wandering Took', 1, 1, 2, 1, 'Spirit', 2)
    dictOfCards['Rider of Rohan'] = Ally(12, 'Rider of Rohan', 2, 0, 2, 2, 'Spirit', 3)
    dictOfCards['Gandalf'] = Ally(15, 'Gandalf', 4, 4, 4, 4, 'Neutral', 5) ### watch out: change id numbers in player.findGandalfInHand() when messing around!!!!!!!!!!!!!!!!!!

    dictOfCards['Flies and Spiders'] = Quest(-1, 'Flies and Spiders', 'Passage through Mirkwood', 8)
    dictOfCards['A fork in the road'] = Quest(-2, 'A fork in the road', 'Passage through Mirkwood', 2)
    dictOfCards['Beorns Path'] = Quest(-3, 'Beorns Path', 'Passage through Mirkwood', 10)

    dictOfCards['Dol Guldur Orcs'] = Enemy(18, 'Dol Guldur Orcs', 2, 0, 3, 10, 2)
    dictOfCards['Dol Guldur Beastmaster'] = Enemy(21, 'Dol Guldur Beastmaster', 3, 1, 5, 35, 2)
    dictOfCards['Forest Spider'] = Enemy(22, 'Forest Spider', 2, 1, 4, 25, 2)
    dictOfCards['East Bight Patrol'] = Enemy(26, 'East Bight Patrol', 3, 1, 2, 5, 3)
    dictOfCards['Black Forest Bats'] = Enemy(27, 'Black Forest Bats', 1, 0, 2, 15, 1)
    dictOfCards['King Spider'] = Enemy(28, 'King Spider', 3, 1, 3, 20, 2)
    dictOfCards['Ungoliants Spawn'] = Enemy(30, 'Ungoliants Spawn', 5, 2, 9, 32, 3)

    dictOfCards['Necromancers Pass'] = Land(31, 'Necromancers Pass', 3, 2)
    dictOfCards['Enchanted Stream'] = Land(32, 'Enchanted Stream', 2, 2)
    dictOfCards['Old Forest Road'] = Land(34, 'Old Forest Road', 1, 3)
    dictOfCards['Forest Gate'] = Land(36, 'Forest Gate', 2, 4)
    dictOfCards['Great Forest Web'] = Land(38, 'Great Forest Web', 2, 2)
    dictOfCards['Mountains of Mirkwood'] = Land(40, 'Mountains of Mirkwood', 2, 3)

    heroes.append(dictOfCards['Dunhere'])
    heroes.append(dictOfCards['Eowyn'])
    heroes.append(dictOfCards['Eleanor'])

    playerDeck = RegularDeck('Player Deck')
    playerDeck.addCopies(dictOfCards['Wandering Took'], 3)
    playerDeck.addCopies(dictOfCards['Lorien Guide'], 3)
    playerDeck.addCopies(dictOfCards['Northern Tracker'], 3)
    playerDeck.addCopies(dictOfCards['Rider of Rohan'], 3)
    playerDeck.addCopies(dictOfCards['Gandalf'], 3)
    decks['Player Deck'] = playerDeck

    global numberOfAllies
    numberOfAllies = 15 ## change when messing with ally cards!!!!!!!!

    questDeck = QuestDeck('Passage through Mirkwood')
    questDeck.addCopies(dictOfCards['Flies and Spiders'], 1)
    if fullGame:
        questDeck.addCopies(dictOfCards['A fork in the road'], 1)
        questDeck.addCopies(dictOfCards['Beorns Path'], 1)
    decks['Quest Deck'] = questDeck

    encounterDeck = RegularDeck('Encounter Deck')
    encounterDeck.addCopies(dictOfCards['Dol Guldur Orcs'], 3)
    encounterDeck.addCopies(dictOfCards['Dol Guldur Beastmaster'], 1)
    encounterDeck.addCopies(dictOfCards['Forest Spider'], 4)
    encounterDeck.addCopies(dictOfCards['East Bight Patrol'], 1)
    encounterDeck.addCopies(dictOfCards['Black Forest Bats'], 1)
    encounterDeck.addCopies(dictOfCards['King Spider'], 2)
    encounterDeck.addCopies(dictOfCards['Ungoliants Spawn'], 1)

    global numberOfEnemies
    numberOfEnemies = 13 ## change when messing with enemy cards!!!!

    if difficulty == 'hard' or difficulty == 'medium':
        encounterDeck.addCopies(dictOfCards['Necromancers Pass'], 1)
        encounterDeck.addCopies(dictOfCards['Enchanted Stream'], 2)
        encounterDeck.addCopies(dictOfCards['Old Forest Road'], 2)
        encounterDeck.addCopies(dictOfCards['Forest Gate'], 2)
        encounterDeck.addCopies(dictOfCards['Great Forest Web'], 2)
        encounterDeck.addCopies(dictOfCards['Mountains of Mirkwood'], 3)
        global numberOfLands
        numberOfLands = 12 ## the same with lands!!!!!

    decks['Encounter Deck'] = encounterDeck


