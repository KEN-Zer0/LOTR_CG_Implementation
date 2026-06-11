from src.cards.base_card import BaseCard


class ProgressObjective(BaseCard):
    """A card that tracks progress tokens and completes when required_progress is reached."""

    def __init__(self, name, required_progress):
        """Initialize with 0 progress.

        Args:
            name (Enum): Enum identifier for this objective.
            required_progress (int): Number of progress tokens needed to complete the objective.
        """
        super().__init__(name)
        self._required_progress = required_progress
        self._progress = 0

    @property
    def progress(self):
        """int: Current number of progress tokens placed on this card."""
        return self._progress

    @property
    def required_progress(self):
        """int: Number of progress tokens needed to complete this objective."""
        return self._required_progress

    def place_progress_token(self, tokens):
        """Add progress tokens to this card.

        Args:
            tokens (int): Number of progress tokens to add.
        """
        self._progress += tokens

    def is_complete(self):
        """Check whether this objective has been completed.

        Returns:
            bool: True when progress has reached or exceeded required_progress.
        """
        return self._progress >= self._required_progress
