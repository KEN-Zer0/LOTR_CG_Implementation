from .phase import Phase
from config.constants import GameConstants
from src.cards import Hero, Ally


class RefreshPhase(Phase):
    """Phase 7 — ready all exhausted characters and raise the player's threat by 1."""

    def execute(self) -> None:
        """Ready all characters and increase table threat by 1."""
        self.ready_player_characters()
        self.raise_threat_level()

    def ready_character(self, character: Hero | Ally) -> None:
        """Remove the exhausted state from a single character."""
        character.ready()

    def ready_player_characters(self) -> None:
        """Ready every hero and ally on the board."""
        for character in self.table.player_heroes + self.table.player_board:
            self.ready_character(character)

    def raise_threat_level(self) -> None:
        """Increase table_threat by 1."""
        self.table.table_threat += GameConstants.THREAT_PER_ROUND
