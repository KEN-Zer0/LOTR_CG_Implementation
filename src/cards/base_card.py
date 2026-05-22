from abc import ABC, abstractmethod


class BaseCard(ABC):
    def __init__(self, name):
        self._name = name


    @property
    def name(self):
        if not self._name:
            return "Name empty"
        return self._name
