from abc import ABC, abstractmethod

from src.table import Table


class Phase(ABC):
    _table: Table

    def __init__(self, table: Table):
        self._table = table

    @abstractmethod
    def executePhase(self):
        pass