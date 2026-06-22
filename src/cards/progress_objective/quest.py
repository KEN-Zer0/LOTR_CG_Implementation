from .progress_objective import ProgressObjective


class Quest(ProgressObjective):
    """A quest card belonging to a specific scenario; completing all quests wins the game."""

    def __init__(self, name, scenario, required_progress):
        """Initialize quest for the given scenario.

        Args:
            name (Enum): Enum identifier for this quest card.
            scenario (Scenario): Scenario this quest card belongs to.
            required_progress (int): Number of progress tokens needed to complete this quest.
        """
        super().__init__(name, required_progress)
        self._scenario = scenario

    @property
    def scenario(self):
        """Scenario: Scenario identifier this quest card belongs to."""
        return self._scenario

    def copy(self):
        """Create a copy of this quest with progress reset to 0.

        Returns:
            Quest: A new Quest instance with the same name, scenario, and required_progress.
        """
        return Quest(
            self.name,
            self.scenario,
            self.required_progress
        )
