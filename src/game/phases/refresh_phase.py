from .phase import Phase


class RefreshPhase(Phase):
    def execute(self):
        self.ready_player_characters()
        self.raise_threat_level()

    def ready_character(self, character):
        character.ready()

    def ready_player_characters(self):
        for _ in self.table.player_engagement:
            for character in _:
                self.ready_character(character)

    def raise_threat_level(self):
        self.table.table_threat += 1