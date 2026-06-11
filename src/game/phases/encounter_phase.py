from .phase import Phase
from src.cards import Enemy


class EncounterPhase(Phase):
    """
    Encounter phase:
    1. Reveal 1 encounter card and place it in the staging area.
    2. Optional engagement: player may voluntarily engage staging enemies.
    3. Forced engagement: staging enemies with engagement cost <= table threat auto-engage.
    """

    def execute(self):
        """Reveal one encounter card, handle optional engagement, then auto-engage eligible enemies."""
        self._reveal_encounter_cards()
        self._optional_engagement()
        self._forced_engagement()

    # --- Reveal ---

    def _reveal_encounter_cards(self) -> None:
        """Reveal the top encounter card and place it in the staging area."""
        self.table.reveal_encounter_card()

    # --- Optional engagement ---

    def _optional_engagement(self) -> None:
        """Engage any enemies chosen by _choose_optional_engagement."""
        available = self._get_staging_enemies()
        chosen = self._choose_optional_engagement(available)
        for enemy in chosen:
            self._engage(enemy)

    def _choose_optional_engagement(self, available: list[Enemy]) -> list[Enemy]:
        """Delegates to the table's agent.

        Args:
            available (list[Enemy]): Enemies currently in the staging area.

        Returns:
            list[Enemy]: Enemies the player chooses to engage voluntarily.
        """
        return self.table.agent.choose_optional_engagement(self.table, available)

    # --- Forced engagement ---

    def _forced_engagement(self) -> None:
        """Engages all staging enemies whose engagement cost <= current table threat."""
        for enemy in self._get_staging_enemies():
            if enemy.engagement <= self.table.table_threat:
                self._engage(enemy)

    # --- Helpers ---

    def _get_staging_enemies(self) -> list[Enemy]:
        return [c for c in self.table.encounter_staging if isinstance(c, Enemy)]

    def _engage(self, enemy: Enemy) -> None:
        self.table.encounter_staging.remove(enemy)
        self.table.encounter_engagement.append(enemy)
