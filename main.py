from src.cards import Hero

gandalf = Hero("Gandalf", 1, 2, 3, 4, 5, 6)

def printHero(hero):
    print(
        hero.name,
        hero.attack,
        hero.defense,
        hero.max_hit_points,
        hero.hit_points,
        hero.willpower,
        hero.sphere_of_influence,
        hero.threat
    )

printHero(gandalf)

gandalf.change_hp(-3)
printHero(gandalf)