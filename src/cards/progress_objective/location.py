from .progress_objective import ProgressObjective

class Location(ProgressObjective):
    def __init__(self, name, threat, progress_token):
        super().__init__(name, progress_token)
        self._threat = threat

    def copy(self):
        return Location(
            self.name,
            self.threat,
            self.progress_token
        )