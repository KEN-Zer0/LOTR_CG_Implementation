from src.cards.base_card import BaseCard


class ProgressObjective(BaseCard):
    """A card that tracks progress tokens and completes when required_progress is reached."""

    def __init__(self, name, required_progress):
        """Initialize with 0 progress."""
        super().__init__(name)
        self._required_progress = required_progress
        self._progress = 0

    @property
    def progress(self):
        """Current number of progress tokens placed on this card."""
        return self._progress

    @property
    def required_progress(self):
        """Number of progress tokens needed to complete this objective."""
        return self._required_progress

    def place_progress_token(self, tokens):
        """Add tokens progress tokens to this card."""
        self._progress += tokens

    def is_complete(self):
        """Return True when progress has reached or exceeded required_progress."""
        return self._progress >= self._required_progress
