from .progress_objective import ProgressObjective


class Location(ProgressObjective):
    """A location in the encounter deck that adds staging threat until cleared."""

    def __init__(self, name, threat, required_progress):
        """Initialize location with a staging threat value."""
        super().__init__(name, required_progress)
        self._threat = threat

    @property
    def threat(self):
        """Staging-area threat added each round while this location is active or in staging."""
        return self._threat

    def copy(self):
        """Return a new Location with same stats (progress reset to 0)."""
        return Location(
            self.name,
            self.threat,
            self.required_progress
        )
