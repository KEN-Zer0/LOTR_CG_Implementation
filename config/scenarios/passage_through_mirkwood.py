from config.scenarios.scenario_setup import ScenarioSetup
from config.limited.cards_list import Enemies

SETUP = ScenarioSetup(
    opening_hand_size=6,
    initial_staging=[Enemies.Ungoliants_Spawn],
)
