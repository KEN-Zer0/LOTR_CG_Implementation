from .progress_objective import ProgressObjective


class Quest(ProgressObjective):
    def __init__(self, name, scenario, required_progress):
        super().__init__(name, required_progress)
        self._scenario = scenario

    @property
    def scenario(self):
        return self._scenario

    def copy(self):
        return Quest(
            self.name,
            self.scenario,
            self.required_progress
        )