from .progress_objective import ProgressObjective

class Location(ProgressObjective):
    def __init__(self, name, threat, required_progress):
        super().__init__(name, required_progress)
        self._threat = threat

    @property
    def threat(self):
        return self._threat

    def copy(self):
        return Location(
            self.name,
            self.threat,
            self.required_progress
        )