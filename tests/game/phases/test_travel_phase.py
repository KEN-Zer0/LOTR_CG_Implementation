import pytest
from src.game.phases.travel_phase import TravelPhase
from src.cards import Location
from config.limited.cards_list import Locations
from config.limited.cards_registry import CARDS


def test_no_travel_when_active_location_exists(table):
    """Travel phase skips when there is already an active location."""
    phase = TravelPhase(table)
    existing = Location(Locations.Forest_Gate, 2, 4)
    table.active_travel_location = existing
    other = Location(Locations.Old_Forest_Road, 1, 3)
    table.encounter_staging.append(other)
    phase.execute()
    assert table.active_travel_location is existing


def test_travels_to_highest_threat_location(table):
    """The location with the highest staging threat is selected."""
    phase = TravelPhase(table)
    low = Location(Locations.Old_Forest_Road, 1, 3)
    high = Location(Locations.Necromancers_Pass, 3, 2)
    table.encounter_staging.extend([low, high])
    phase.execute()
    assert table.active_travel_location is high


def test_location_removed_from_staging_on_travel(table):
    """Chosen location leaves the staging area and becomes the active location."""
    phase = TravelPhase(table)
    loc = Location(Locations.Forest_Gate, 2, 4)
    table.encounter_staging.append(loc)
    phase.execute()
    assert loc not in table.encounter_staging
    assert table.active_travel_location is loc


def test_no_travel_when_staging_has_no_locations(table):
    """Active location remains None when no locations are in the staging area."""
    phase = TravelPhase(table)
    table.encounter_staging.clear()
    phase.execute()
    assert table.active_travel_location is None


def test_choose_location_returns_highest_threat(table):
    """_choose_location picks the location with the highest threat value."""
    phase = TravelPhase(table)
    low = Location(Locations.Old_Forest_Road, 1, 3)
    high = Location(Locations.Necromancers_Pass, 3, 2)
    assert phase._choose_location([low, high]) is high


def test_can_afford_travel_zero_cost(table):
    """Locations with no travel cost are always affordable."""
    phase = TravelPhase(table)
    loc = Location(Locations.Forest_Gate, 2, 4)
    assert phase._can_afford_travel(loc) is True


def test_travel_cost_exhausts_one_hero(table):
    """Travelling to a location with travel_cost=1 exhausts exactly one ready hero."""
    phase = TravelPhase(table)
    loc = CARDS[Locations.Forest_Gate].copy()
    loc.travel_cost = 1
    table.encounter_staging.append(loc)
    ready_before = sum(1 for h in table.player_heroes if not h.exhausted)
    phase.execute()
    ready_after = sum(1 for h in table.player_heroes if not h.exhausted)
    assert table.active_travel_location is loc
    assert ready_before - ready_after == 1


def test_high_travel_cost_excludes_location_from_eligible(table):
    """Location requiring more heroes than available is not eligible to travel."""
    phase = TravelPhase(table)
    loc = CARDS[Locations.Forest_Gate].copy()
    loc.travel_cost = 10  # only 3 heroes ready
    table.encounter_staging.append(loc)
    phase.execute()
    assert table.active_travel_location is None
    assert loc in table.encounter_staging
