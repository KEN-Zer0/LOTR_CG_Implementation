import pytest
from src.cards.creatures.enemy import Enemy


def test_enemy_initialization():
    enemy = Enemy(
        name="Goblin",
        attack=2,
        defense=1,
        hitMaxPoints=5,
        hitPoints=5,
        engagement=10,
        threat=3
    )

    assert enemy.name == "Goblin"
    assert enemy.attack == 2
    assert enemy.defense == 1
    assert enemy.engagement == 10
    assert enemy.threat == 3


def test_enemy_properties():
    enemy = Enemy(
        "Orc", 3, 2, 8, 8, engagement=15, threat=4
    )

    assert enemy.engagement == 15
    assert enemy.threat == 4


def test_enemy_copy_creates_independent_object():
    enemy = Enemy("Troll", 5, 4, 10, 10, engagement=20, threat=6)

    enemy_copy = enemy.copy()

    assert enemy_copy is not enemy
    assert enemy_copy.name == enemy.name
    assert enemy_copy.hitPoints == enemy.hitPoints