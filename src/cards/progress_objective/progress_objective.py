from src.cards.base_card import BaseCard


class ProgressObjective(BaseCard):
    def __init__(self, name, required_progress):
        super().__init__(name)
        self._required_progress = required_progress
        self._progress = 0

    @property
    def progress(self):
        return self._progress

    def place_progress_token(self, tokens):
        self._progress += tokens

    def is_complete(self):
        return self._progress >= self._required_progress