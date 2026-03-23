from Game_Model.player_creature import PlayerCreature

class Ally(PlayerCreature):
    def __init__(self, id, name, attack, defense, hitpoints, willpower, sphere, cost):
        super(Ally, self).__init__(id, name, attack, defense, hitpoints, willpower, sphere)
        self.cost = cost

    def getCost(self):
        return self.cost

    def copy(self):
        newAlly = Ally(self.id, self.name, self.attack, self.defense, self.hitpoints, self.willpower, self.sphere, self.cost)
        return newAlly
