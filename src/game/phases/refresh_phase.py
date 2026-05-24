from .phase import Phase


class RefreshPhase(Phase):
    def execute(self):
        self.ready_player_characters()
        self.raise_threat_level()

    def ready_character(self, character):
        character.ready()

    def ready_player_characters(self):
        all_characters = (
                self.table.player_heroes
                + self.table.player_board
                + self.table.questing
                + self.table.attacking
                + self.table.defending
        )
        for character in all_characters:
            self.ready_character(character)

    def raise_threat_level(self):
        self.table.table_threat += 1