class Card:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.status = 0

    def getId(self):
        return self.id

    def setId(self, id):
        self.id = id

    def getName(self):
        return self.name

    def getStatus(self):
        return self.status

    def setStatus(self, stat): # watch out!!!!!!!!!!!!
        self.status = stat
