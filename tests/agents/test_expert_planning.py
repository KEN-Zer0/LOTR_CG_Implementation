import pytest

from agents.expert_agent import ExpertAgent
from config.limited.cards_registry import CARDS
from config.limited.cards_list import Allies, Enemies, Locations


@pytest.fixture
def agent():
    return ExpertAgent()


# ── choose_card_to_play ────────────────────────────────────────────────────

def test_picks_cheapest_card(agent, table):
    cheap  = CARDS[Allies.Wandering_Took].copy()    # cost=2
    expensive = CARDS[Allies.Northern_Tracker].copy()  # cost=4
    assert agent.choose_card_to_play(table, [expensive, cheap]) is cheap


def test_single_card_returned(agent, table):
    card = CARDS[Allies.Gandalf].copy()
    assert agent.choose_card_to_play(table, [card]) is card


def test_picks_cheapest_among_three(agent, table):
    c2 = CARDS[Allies.Gondorian_Spearman].copy()  # cost=2
    c3 = CARDS[Allies.Lorien_Guide].copy()         # cost=3
    c6 = CARDS[Allies.Beorn].copy()                # cost=6
    assert agent.choose_card_to_play(table, [c6, c3, c2]) is c2


# ── choose_location ────────────────────────────────────────────────────────

def test_picks_location_with_highest_threat(agent, table):
    low  = CARDS[Locations.Old_Forest_Road].copy()        # threat=1
    high = CARDS[Locations.Necromancers_Pass].copy()      # threat=3
    assert agent.choose_location(table, [low, high]) is high


def test_single_location_returned(agent, table):
    loc = CARDS[Locations.Forest_Gate].copy()
    assert agent.choose_location(table, [loc]) is loc


def test_picks_highest_among_all_locations(agent, table):
    locs = [CARDS[loc].copy() for loc in Locations]
    result = agent.choose_location(table, locs)
    assert result.threat == max(l.threat for l in locs)


# ── choose_optional_engagement ─────────────────────────────────────────────

def test_never_engages_voluntarily(agent, table):
    enemies = [CARDS[Enemies.Dol_Guldur_Orcs].copy()]
    assert agent.choose_optional_engagement(table, enemies) == []


def test_never_engages_with_multiple_enemies(agent, table):
    enemies = [CARDS[e].copy() for e in Enemies]
    assert agent.choose_optional_engagement(table, enemies) == []


def test_never_engages_empty_input(agent, table):
    assert agent.choose_optional_engagement(table, []) == []
