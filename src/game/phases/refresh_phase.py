from .phase import Phase


class RefreshPhase(Phase):
    def executePhase(self):
        super().executePhase()

        self.ready_player_characters()
        self.raise_threat_level()

    def ready_character(self, character):
        character.ready()

    def ready_player_characters(self):
        for _ in self._table.player_engagement:
            for character in _:
                self.ready_character(character)

    def raise_threat_level(self):
        self._table.table_threat += 1