import pytest
from src.cards.creatures.player_creatures import PlayerCreature


def create_hero():
    """Helper function to create a test PlayerCreature."""
    return PlayerCreature(
        name="Aragorn",
        attack=3,
        defense=2,
        max_hit_points=5,
        willpower=2,
        sphere_of_influence="Leadership"
    )


def test_player_creature_init():
    """Verify attributes are set correctly after init."""
    hero = create_hero()
    assert hero.name == "Aragorn"
    assert hero.willpower == 2
    assert hero.sphere_of_influence == "Leadership"
    assert hero.exhausted is False  # Should be ready by default


def test_exhaust_mechanism():
    """Test if card can be exhausted and readied again."""
    hero = create_hero()

    # 1. Exhaust the card
    hero.exhaust()
    assert hero.is_exhausted() is True
    assert hero.exhausted is True

    # 2. Ready the card
    hero.ready()
    assert hero.is_exhausted() is False
    assert hero.exhausted is False


def test_is_alive_at_zero_hp():
    """Verify that creature at exactly 0 HP is considered dead (is_alive returns False)."""
    hero = create_hero()

    hero._hit_points = 0
    assert hero.is_alive() is False


def test_is_dead_below_zero():
    """Verify creature is dead when HP is negative."""
    hero = create_hero()

    # Simulate lethal damage
    hero._hit_points = -1
    assert hero.is_alive() is False


def test_properties_are_read_only():
    """Ensure willpower and sphere cannot be changed directly."""
    hero = create_hero()

    with pytest.raises(AttributeError):
        hero.willpower = 5

    with pytest.raises(AttributeError):
        hero.sphere_of_influence = "Lore"