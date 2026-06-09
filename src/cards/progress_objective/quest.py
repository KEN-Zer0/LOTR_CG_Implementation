from .progress_objective import ProgressObjective


class Quest(ProgressObjective):
    """A quest card belonging to a specific scenario; completing all quests wins the game."""

    def __init__(self, name, scenario, required_progress):
        """Initialize quest for the given scenario."""
        super().__init__(name, required_progress)
        self._scenario = scenario

    @property
    def scenario(self):
        """Scenario identifier this quest card belongs to."""
        return self._scenario

    def copy(self):
        """Return a new Quest with same name, scenario, and required_progress (progress reset to 0)."""
        return Quest(
            self.name,
            self.scenario,
            self.required_progress
        )
