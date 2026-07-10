"""Standardized description of scenario setup rules.

A ScenarioSetup declares what needs to happen before the first round:
how many cards the player draws as an opening hand, and which cards
are pulled from the encounter deck and placed directly in the staging area.

To add a new scenario:
1. Create config/scenarios/<scenario_name>.py that defines a module-level
   SETUP = ScenarioSetup(...) with the appropriate values.
2. Register it in config/scenarios/__init__.py under SCENARIOS.

The apply_setup() function is the only place that knows how to execute
these declarations against a live Table — scenario modules stay pure data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.table import Table


@dataclass
class ScenarioSetup:
    """Declarative description of a scenario's initial game state.

    Attributes:
        opening_hand_size: Cards drawn to player hand before the first round.
        initial_staging: Enemy/Location enum values pulled from the encounter
            deck and placed in the staging area as part of setup.
    """

    opening_hand_size: int = 6
    initial_staging: list[Enum] = field(default_factory=list)


def apply_setup(table: Table, setup: ScenarioSetup) -> None:
    """Apply a ScenarioSetup to a live Table.

    Draws the opening hand and moves initial staging cards out of the
    encounter deck.

    Args:
        table: The Table instance to mutate.
        setup: The ScenarioSetup to apply.
    """
    for _ in range(setup.opening_hand_size):
        table.draw_player_card()

    for card_name in setup.initial_staging:
        card = next((c for c in table.encounter_deck if c.name == card_name), None)
        if card:
            table.encounter_deck.remove(card)
            table.encounter_staging.append(card)
