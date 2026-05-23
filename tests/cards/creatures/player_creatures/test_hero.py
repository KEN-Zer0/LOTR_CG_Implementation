import pytest
from src.cards import Hero


def create_legolas():
    """Helper to create a Hero instance."""
    return Hero(
        name="Legolas",
        attack=3,
        defense=1,
        max_hit_points=4,
        willpower=1,
        sphere_of_influence="Tactics",
        threat=9
    )


def test_hero_init():
    """Check if hero starts with threat and empty resource pool."""
    legolas = create_legolas()
    assert legolas.name == "Legolas"
    assert legolas.threat == 9
    assert legolas.resource_pool == 0


def test_add_resource_token():
    """Verify resource pool increases by 1."""
    legolas = create_legolas()
    legolas.add_resource_token()
    assert legolas.resource_pool == 1
    legolas.add_resource_token()
    assert legolas.resource_pool == 2


def test_change_resource_pool_positive():
    """Check adding resources via delta."""
    legolas = create_legolas()
    legolas.change_resource_pool(5)
    assert legolas.resource_pool == 5


def test_change_resource_pool_negative():
    """Check spending resources and ensuring it doesn't go below 0."""
    legolas = create_legolas()
    legolas.change_resource_pool(3)

    # Spend 2
    legolas.change_resource_pool(-2)
    assert legolas.resource_pool == 1

    # Try to spend more than available
    legolas.change_resource_pool(-10)
    assert legolas.resource_pool == 0  # Should be capped at 0


def test_hero_copy():
    """Verify copy creates a new hero with same threat and resources."""
    legolas = create_legolas()
    legolas.change_resource_pool(3)

    legolas_copy = legolas.copy()

    assert legolas_copy is not legolas
    assert legolas_copy.name == legolas.name
    assert legolas_copy.threat == 9
    assert legolas_copy.resource_pool == 3


def test_threat_is_read_only():
    """Threat should not be modified directly after setup."""
    legolas = create_legolas()
    with pytest.raises(AttributeError):
        legolas.threat = 10