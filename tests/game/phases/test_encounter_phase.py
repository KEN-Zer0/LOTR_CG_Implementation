import pytest
from src.game.phases.encounter_phase import EncounterPhase
from src.cards import Enemy, Location
from config.limited.cards_list import Enemies, Locations
from config.limited.cards_registry import CARDS


def test_execute_reveals_one_card_into_staging(table):
    """One card is moved from the encounter deck to the staging area."""
    phase = EncounterPhase(table)
    deck_before = len(table.encounter_deck)
    phase._reveal_encounter_cards()
    assert len(table.encounter_deck) == deck_before - 1
    assert len(table.encounter_staging) == 1


def test_forced_engagement_when_threat_high_enough(table):
    """Enemy with engagement <= table_threat moves from staging to engagement."""
    phase = EncounterPhase(table)
    enemy = Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2)  # engagement=10
    table.encounter_staging.append(enemy)
    table.table_threat = 25  # 25 >= 10 → engages
    phase._forced_engagement()
    assert enemy in table.encounter_engagement
    assert enemy not in table.encounter_staging


def test_no_forced_engagement_when_threat_too_low(table):
    """Enemy with engagement > table_threat stays in the staging area."""
    phase = EncounterPhase(table)
    enemy = Enemy(Enemies.Chieftan_Ufthak, 3, 3, 6, 35, 2)  # engagement=35
    table.encounter_staging.append(enemy)
    table.table_threat = 25  # 25 < 35 → does not engage
    phase._forced_engagement()
    assert enemy not in table.encounter_engagement
    assert enemy in table.encounter_staging


def test_optional_engagement_default_returns_empty(table):
    """Default implementation of _choose_optional_engagement returns no enemies."""
    phase = EncounterPhase(table)
    enemy = Enemy(Enemies.Forest_Spider, 2, 1, 4, 25, 2)
    assert phase._choose_optional_engagement([enemy]) == []


def test_engage_moves_enemy_to_engagement(table):
    """_engage removes enemy from staging and adds it to encounter_engagement."""
    phase = EncounterPhase(table)
    enemy = Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2)
    table.encounter_staging.append(enemy)
    phase._engage(enemy)
    assert enemy in table.encounter_engagement
    assert enemy not in table.encounter_staging


def test_get_staging_enemies_excludes_locations(table):
    """_get_staging_enemies returns only Enemy instances, not Locations."""
    phase = EncounterPhase(table)
    table.encounter_staging.clear()
    enemy = Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2)
    loc = Location(Locations.Forest_Gate, 2, 4)
    table.encounter_staging.extend([enemy, loc])
    result = phase._get_staging_enemies()
    assert enemy in result
    assert loc not in result


def test_location_in_staging_never_force_engaged(table):
    """Locations are never moved to encounter_engagement by forced engagement."""
    phase = EncounterPhase(table)
    loc = CARDS[Locations.Great_Forest_Web].copy()
    table.encounter_staging.append(loc)
    table.table_threat = 50
    phase._forced_engagement()
    assert loc not in table.encounter_engagement
    assert loc in table.encounter_staging
