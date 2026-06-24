import pytest
from agents.base_agent import BaseAgent
from agents.logging_agent import LoggingAgent
from config.limited.cards_registry import CARDS
from config.limited.cards_list import Allies, Enemies, Locations
from src.logging.logger import Logger


class _FixedAgent(BaseAgent):
    """Stub agent with controllable return values."""
    def __init__(self, quester=None, card=None, location=None,
                 engagements=None, defender=None, undefended=None, attackers=None):
        self._quester     = quester
        self._card        = card
        self._location    = location
        self._engagements = engagements or []
        self._defender    = defender
        self._undefended  = undefended
        self._attackers   = attackers or []

    def choose_questing_characters(self, gs, available):   return [self._quester] if self._quester else []
    def choose_card_to_play(self, gs, playable):           return self._card
    def choose_location(self, gs, eligible):               return self._location
    def choose_optional_engagement(self, gs, available):   return self._engagements
    def choose_defender(self, gs, enemy, available):       return self._defender
    def choose_undefended_target(self, gs, enemy):         return self._undefended
    def choose_attackers(self, gs, enemy, available):      return self._attackers


@pytest.fixture(autouse=True)
def reset_logger():
    Logger.enable()
    yield
    Logger.close()


@pytest.fixture
def hero(table):
    return table.player_heroes[0]


@pytest.fixture
def ally():
    return CARDS[Allies.Gondorian_Spearman].copy()


@pytest.fixture
def enemy():
    return CARDS[Enemies.Dol_Guldur_Orcs].copy()


@pytest.fixture
def location():
    return CARDS[Locations.Forest_Gate].copy()


class TestLoggingAgentDelegation:
    def test_questing_returns_wrapped_result(self, table, hero):
        agent = LoggingAgent(_FixedAgent(quester=hero))
        assert agent.choose_questing_characters(table, [hero]) == [hero]

    def test_card_to_play_returns_card(self, table, ally):
        agent = LoggingAgent(_FixedAgent(card=ally))
        assert agent.choose_card_to_play(table, [ally]) is ally

    def test_card_to_play_returns_none(self, table, ally):
        agent = LoggingAgent(_FixedAgent(card=None))
        assert agent.choose_card_to_play(table, [ally]) is None

    def test_location_returns_location(self, table, location):
        agent = LoggingAgent(_FixedAgent(location=location))
        assert agent.choose_location(table, [location]) is location

    def test_location_returns_none(self, table, location):
        agent = LoggingAgent(_FixedAgent(location=None))
        assert agent.choose_location(table, [location]) is None

    def test_optional_engagement_returns_list(self, table, enemy):
        agent = LoggingAgent(_FixedAgent(engagements=[enemy]))
        assert agent.choose_optional_engagement(table, [enemy]) == [enemy]

    def test_defender_returns_defender(self, table, hero, enemy):
        agent = LoggingAgent(_FixedAgent(defender=hero))
        assert agent.choose_defender(table, enemy, [hero]) is hero

    def test_defender_returns_none(self, table, hero, enemy):
        agent = LoggingAgent(_FixedAgent(defender=None))
        assert agent.choose_defender(table, enemy, [hero]) is None

    def test_undefended_target_returns_hero(self, table, hero, enemy):
        agent = LoggingAgent(_FixedAgent(undefended=hero))
        assert agent.choose_undefended_target(table, enemy) is hero

    def test_attackers_returns_list(self, table, hero, enemy):
        agent = LoggingAgent(_FixedAgent(attackers=[hero]))
        assert agent.choose_attackers(table, enemy, [hero]) == [hero]

    def test_attackers_returns_empty(self, table, hero, enemy):
        agent = LoggingAgent(_FixedAgent(attackers=[]))
        assert agent.choose_attackers(table, enemy, [hero]) == []


class TestLoggingAgentOutput:
    def test_played_card_logged(self, table, ally, capsys):
        LoggingAgent(_FixedAgent(card=ally)).choose_card_to_play(table, [ally])
        assert "played" in capsys.readouterr().out

    def test_planning_pass_logged(self, table, ally, capsys):
        LoggingAgent(_FixedAgent(card=None)).choose_card_to_play(table, [ally])
        assert "pass" in capsys.readouterr().out

    def test_travel_to_logged(self, table, location, capsys):
        LoggingAgent(_FixedAgent(location=location)).choose_location(table, [location])
        assert "travel to" in capsys.readouterr().out

    def test_travel_pass_logged(self, table, location, capsys):
        LoggingAgent(_FixedAgent(location=None)).choose_location(table, [location])
        assert "pass" in capsys.readouterr().out

    def test_defender_logged(self, table, hero, enemy, capsys):
        LoggingAgent(_FixedAgent(defender=hero)).choose_defender(table, enemy, [hero])
        assert "defender" in capsys.readouterr().out

    def test_undefended_attack_logged(self, table, hero, enemy, capsys):
        LoggingAgent(_FixedAgent(defender=None)).choose_defender(table, enemy, [hero])
        assert "undefended" in capsys.readouterr().out

    def test_undefended_target_logged(self, table, hero, enemy, capsys):
        LoggingAgent(_FixedAgent(undefended=hero)).choose_undefended_target(table, enemy)
        assert "undefended attack target" in capsys.readouterr().out

    def test_attackers_logged(self, table, hero, enemy, capsys):
        LoggingAgent(_FixedAgent(attackers=[hero])).choose_attackers(table, enemy, [hero])
        assert "attack on" in capsys.readouterr().out

    def test_no_attackers_logged(self, table, hero, enemy, capsys):
        LoggingAgent(_FixedAgent(attackers=[])).choose_attackers(table, enemy, [hero])
        assert "no attack" in capsys.readouterr().out

    def test_optional_engagement_logged(self, table, enemy, capsys):
        LoggingAgent(_FixedAgent(engagements=[enemy])).choose_optional_engagement(table, [enemy])
        assert "optional engagement" in capsys.readouterr().out
