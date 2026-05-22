from .progress_objective import ProgressObjective


class Quest(ProgressObjective):
    def __init__(self, name, scenario, progress_token):
        super().__init__(name, progress_token)
        self._scenario = scenario

    def copy(self):
        return Quest(
            self.name,
            self.scenario,
            self.progress_token
        )