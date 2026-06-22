from abc import ABC


class BaseCard(ABC):
    """Base class for all card types."""

    def __init__(self, name):
        """Initialize the card.

        Args:
            name (Enum): Enum identifier for this card.
        """
        self._name = name

    @property
    def name(self):
        """Return the card's enum identifier, or the string "Name empty" if unset.

        Returns:
            Enum | str: The card name enum or a fallback string.
        """
        if not self._name:
            return "Name empty"
        return self._name