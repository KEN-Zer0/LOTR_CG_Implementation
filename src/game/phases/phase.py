from abc import ABC, abstractmethod

from src.table import Table


class Phase(ABC):
    table: Table

    def __init__(self, table: Table):
        self.table = table

    @abstractmethod
    def execute(self):
        pass