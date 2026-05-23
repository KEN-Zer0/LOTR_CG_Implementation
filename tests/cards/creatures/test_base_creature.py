import pytest

# Import classes from your project structure
from src.cards.creatures.base_creature import Creature


@pytest.fixture
def default_creature():
    """Returns a fresh Creature instance before each test."""
    return Creature(name="Orc Warrior", attack=3, defense=1, max_hit_points=5)


def test_creature_initialization(default_creature):
    # Check attributes and properties after creation
    assert default_creature.name == "Orc Warrior"
    assert default_creature.attack == 3
    assert default_creature.defense == 1
    assert default_creature.max_hit_points == 5
    assert default_creature.hit_points == 5  # HP equals max HP at start


def test_creature_is_not_dead_initially(default_creature):
    # New creature must be alive
    assert default_creature.is_dead() is False


def test_change_hp_damage(default_creature):
    # Reduce HP and check current value
    default_creature.change_hp(-2)
    assert default_creature.hit_points == 3
    assert default_creature.is_dead() is False


def test_change_hp_lethal_damage(default_creature):
    # Reduce HP to exactly 0 and check if dead
    default_creature.change_hp(-5)
    assert default_creature.hit_points == 0
    assert default_creature.is_dead() is True


def test_change_hp_drops_below_zero(default_creature):
    # HP should stop at 0 and not become negative
    default_creature.change_hp(-10)
    assert default_creature.hit_points == 0
    assert default_creature.is_dead() is True


def test_change_hp_healing(default_creature):
    # Damage creature then heal it
    default_creature.change_hp(-3)  # Drops to 2
    default_creature.change_hp(2)  # Rises to 4
    assert default_creature.hit_points == 4


def test_change_hp_overhealing(default_creature):
    # HP should not exceed max_hit_points
    default_creature.change_hp(-1)  # Drops to 4
    default_creature.change_hp(10)  # Try to heal above max
    assert default_creature.hit_points == 5  # Capped at max_hit_points


@pytest.mark.parametrize(
    "delta, expected_hp, expected_is_dead",
    [
        (0, 5, False),  # No change
        (-2, 3, False),  # Normal damage
        (-5, 0, True),  # Exact lethal damage
        (-10, 0, True),  # Excess damage (floor at 0)
        (5, 5, False),  # Healing at full health (cap at max)
    ],
)
def test_creature_hp_edges(delta, expected_hp, expected_is_dead):
    # Test multiple HP change scenarios and boundary values
    c = Creature("Test Creature", attack=1, defense=1, max_hit_points=5)
    c.change_hp(delta)
    assert c.hit_points == expected_hp
    assert c.is_dead() == expected_is_dead