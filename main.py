class Card():
    def __init__(self, Name):
        self.Name = Name

    def setName(self, Name):
        self.Name = Name

    def getName(self):
        return self.Name

Gandalf = Card('Gandalf')

print(Gandalf.getName())