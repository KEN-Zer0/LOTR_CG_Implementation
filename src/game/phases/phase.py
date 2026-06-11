from abc import ABC, abstractmethod

from src.table import Table


class Phase(ABC):
    """Abstract base class for all game phases."""

    table: Table

    def __init__(self, table: Table):
        """Attach the shared Table instance used by all phase operations."""
        self.table = table

    @abstractmethod
    def execute(self):
        """Run this phase to completion; must be implemented by each subclass."""
        pass
