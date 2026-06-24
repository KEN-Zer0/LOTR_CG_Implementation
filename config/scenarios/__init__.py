from config.limited.cards_list import Scenario
from config.scenarios.scenario_setup import ScenarioSetup, apply_setup
from config.scenarios import passage_through_mirkwood

SCENARIOS: dict[Scenario, ScenarioSetup] = {
    Scenario.Passage_through_Mirkwood: passage_through_mirkwood.SETUP,
}
