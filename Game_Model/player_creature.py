from Game_Model.creature import Creature

class PlayerCreature(Creature):
    def __init__(self, id,  name, attack, defense, hitpoints, willpower, sphere):
        super(PlayerCreature, self).__init__(id, name, attack, defense, hitpoints)
        self.willpower = willpower
        self.sphere = sphere
        self.tapped = False

    def getWillpower(self):
        return self.willpower

    def getSphere(self):
        return self.sphere

    def isTapped(self):
        return self.tapped

    def tap(self):
        self.tapped = True

    def untap(self):
        self.tapped = False
