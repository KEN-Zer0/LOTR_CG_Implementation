from src.cards.creatures.player_creatures import Hero

gandalf = Hero("Gandalf", 1, 2, 3, 4, 5, 6, 7)

def printHero(hero):
    print(
        hero.name,
        hero.attack,
        hero.defense,
        hero.hitMaxPoints,
        hero.hitPoints,
        hero.willpower,
        hero.sphere,
        hero.threat
    )

printHero(gandalf)