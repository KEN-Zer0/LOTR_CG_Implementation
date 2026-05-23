import pytest

from src.cards import Enemy


@pytest.fixture
def default_enemy():
    """Returns a fresh Enemy instance before each test."""
    return Enemy(
        name="Goblin Scout",
        attack=2,
        defense=1,
        max_hit_points=3,
        engagement=25,
        threat=2,
    )


def test_enemy_initialization(default_enemy):
    # Check if all attributes and properties are set correctly
    assert default_enemy.name == "Goblin Scout"
    assert default_enemy.attack == 2
    assert default_enemy.defense == 1
    assert default_enemy.max_hit_points == 3
    assert default_enemy.hit_points == 3  # Inherited from Creature
    assert default_enemy.engagement == 25
    assert default_enemy.threat == 2


def test_enemy_copy(default_enemy):
    # Create a copy of the enemy
    enemy_copy = default_enemy.copy()

    # Check if the copy is a different object in memory
    assert enemy_copy is not default_enemy

    # Check if all values were copied correctly
    assert enemy_copy.name == default_enemy.name
    assert enemy_copy.attack == default_enemy.attack
    assert enemy_copy.defense == default_enemy.defense
    assert enemy_copy.max_hit_points == default_enemy.max_hit_points
    assert enemy_copy.engagement == default_enemy.engagement
    assert enemy_copy.threat == default_enemy.threat