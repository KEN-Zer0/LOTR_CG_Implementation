import pytest
from src.game.phases.quest_phase import QuestPhase
from config.limited.cards_list import Enemies, Locations, Allies
from config.limited.cards_registry import CARDS


def test_all_characters_exhausted_after_commit(table):
    """All ready heroes are exhausted when committing to the quest."""
    phase = QuestPhase(table)
    phase.execute()
    for hero in table.player_heroes:
        assert hero.exhausted


def test_willpower_exceeds_threat_adds_progress(table):
    """Net positive willpower adds progress to the active quest."""
    phase = QuestPhase(table)
    quest = table.get_current_quest()
    initial = quest.progress
    phase.execute()
    assert quest.progress > initial


def test_threat_exceeds_willpower_raises_table_threat(table):
    """Net negative willpower raises table_threat by the difference."""
    phase = QuestPhase(table)
    # Heroes willpower = 4+1+1 = 6; add enemies with total threat = 20
    for _ in range(10):
        table.encounter_staging.append(CARDS[Enemies.Dol_Guldur_Orcs].copy())
    initial = table.table_threat
    phase.execute()
    assert table.table_threat > initial


def test_equal_willpower_and_threat_no_change(table):
    """When willpower equals staging threat, neither progress nor threat changes."""
    phase = QuestPhase(table)
    # Heroes willpower = 6; add enemies with total threat = 6
    for _ in range(3):
        table.encounter_staging.append(CARDS[Enemies.Dol_Guldur_Orcs].copy())
    initial_threat = table.table_threat
    initial_progress = table.get_current_quest().progress
    phase.execute()
    assert table.table_threat == initial_threat
    assert table.get_current_quest().progress == initial_progress


def test_quest_advances_when_complete(table):
    """Quest deck shrinks when the current quest accumulates enough progress."""
    phase = QuestPhase(table)
    quest = table.get_current_quest()
    quest._progress = quest.required_progress - 1
    initial_count = len(table.quest_deck)
    phase.execute()
    assert len(table.quest_deck) < initial_count


def test_progress_fills_active_location_first(table):
    """Progress tokens go to the active location before the quest card."""
    phase = QuestPhase(table)
    loc = CARDS[Locations.Old_Forest_Road].copy()  # threat=1, required_progress=3; net willpower=6 > 3 → completes
    table.active_travel_location = loc
    phase.execute()
    assert loc.is_complete()
    assert table.active_travel_location is None
    assert loc in table.encounter_discard


def test_progress_overflow_from_location_to_quest(table):
    """Surplus progress after filling a location carries over to the quest."""
    phase = QuestPhase(table)
    loc = CARDS[Locations.Old_Forest_Road].copy()  # required_progress=3; net willpower=6 → overflow=3
    table.active_travel_location = loc
    quest = table.get_current_quest()
    initial_progress = quest.progress
    # willpower=6, staging threat=0 → net=6; location needs 3 → overflow 3 to quest
    phase.execute()
    assert quest.progress == initial_progress + 3


def test_progress_overflow_from_quest_to_next_quest(table):
    """Excess progress tokens cascade through quests until a quest absorbs them."""
    phase = QuestPhase(table)
    quest = table.get_current_quest()
    quest._progress = quest.required_progress - 1  # 1 token fills quest 1 (req=8), overflow=5
    initial_deck_size = len(table.quest_deck)
    phase.execute()
    # overflow=5 also completes quest 2 (req=2), remaining 3 land on quest 3 (req=10)
    assert len(table.quest_deck) < initial_deck_size
    assert table.get_current_quest().progress == 3


def test_questing_list_cleared_after_phase(table):
    """The questing list is empty after execute completes."""
    phase = QuestPhase(table)
    phase.execute()
    assert table.questing == []


def test_ally_on_board_also_quests(table):
    """Ally on the player board commits to the quest and becomes exhausted."""
    phase = QuestPhase(table)
    ally = CARDS[Allies.Wandering_Took].copy()
    table.player_board.append(ally)
    phase.execute()
    assert ally.exhausted


def test_ally_willpower_adds_to_progress(table):
    """Ally willpower is included in the total willpower during questing."""
    phase = QuestPhase(table)
    ally = CARDS[Allies.Wandering_Took].copy()  # willpower=1
    table.player_board.append(ally)
    quest = table.get_current_quest()
    initial = quest.progress
    # heroes willpower = 4+1+1 = 6, ally willpower = 1, staging threat = 0 → net = +7
    phase.execute()
    assert quest.progress == initial + 7
