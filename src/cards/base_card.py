from abc import ABC


class BaseCard(ABC):
    """
    Base class for all card types.

    Parameters
    ----------
    name : Enum
        The enum representation of the card name.

    Attributes
    ----------
    _name : Enum
        Internal storage for the card name.
    """

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        """
        Get the name of the card.

        Returns
        -------
        Enum or str
            The card name enum, or "Name empty" if the name is not set.
        """
        if not self._name:
            return "Name empty"
        return self._name