from enum import Enum

from .progress_objective import ProgressObjective


class Location(ProgressObjective):
    """A location in the encounter deck that adds staging threat until cleared."""

    def __init__(self, name: Enum, threat: int, required_progress: int) -> None:
        """Initialize location with a staging threat value.

        Args:
            name (Enum): Enum identifier for this location.
            threat (int): Staging-area threat added each round while active or in staging.
            required_progress (int): Number of progress tokens needed to clear this location.
        """
        super().__init__(name, required_progress)
        self._threat = threat

    @property
    def threat(self) -> int:
        """int: Staging-area threat added each round while this location is active or in staging."""
        return self._threat

    def copy(self):
        """Create a copy of this location with progress reset to 0.

        Returns:
            Location: A new Location instance with the same name, threat, and required_progress.
        """
        return Location(
            self.name,
            self.threat,
            self.required_progress
        )
