from abc import ABC


class BaseCard(ABC):
    """
    Klasa bazowa wszystkich kart

    Parameters
    ----------
    name : enum
        enum na nazwę karty

    Attributes
    ----------
    name : enum
        enum na nazwę karty

    Methods
    -------
    name()
        Zwraca name.
    """
    def __init__(self, name):
        self._name = name


    @property
    def name(self):
        """
        Zwraca name.

        Parameters
        ----------
        none

        Raises
        ------
        none

        Returns
        -------
        enum
            Enum na nazwę karty.
        """
        if not self._name:
            return "Name empty"
        return self._name
