import pytest

from src.cards import Hero, Ally, Enemy, Location, Quest
from config.cards_list import Heroes, Allies, Enemies, Locations, Quests, Sphere, Scenario
from src.table.table import Table


@pytest.fixture
def table():
    """Table with fresh hero objects to avoid sharing state with the module-level pool."""
    t = Table()
    t.player_heroes = [
        Hero(Heroes.Eowyn, 1, 1, 3, 4, Sphere.Spirit, 9),
        Hero(Heroes.Eleanor, 1, 2, 3, 1, Sphere.Spirit, 7),
        Hero(Heroes.Thalin, 2, 2, 4, 1, Sphere.Tactics, 9),
    ]
    t.calculate_table_threat()
    return t
