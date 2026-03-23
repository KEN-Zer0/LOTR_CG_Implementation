from Game_Model.card import Card

class Creature(Card):
    def __init__(self, id,  name, attack, defense, hitpoints):
        super(Creature, self).__init__(id, name)
        self.attack = attack
        self.defense = defense
        self.hitpoints = hitpoints
        self.defaultHitpoints = hitpoints

    def getAttack(self):
        return self.attack

    def getDefense(self):
        return self.defense

    def getHitpoints(self):
        return self.hitpoints

    def setHitpoints(self, hitpoints):
        self.hitpoints = hitpoints

    def restoreDefaultHitpoints(self):
        self.hitpoints = self.defaultHitpoints

    def isDead(self):
        return self.getHitpoints() <= 0

    def takeDamage(self, damage):
        self.hitpoints -= damage
