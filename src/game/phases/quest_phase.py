from .phase import Phase
from src.cards import Hero, Ally, Location, Quest


class QuestPhase(Phase):
    """
    Quest phase — characters commit to the quest, then willpower is compared
    against threat from the staging area to determine progress or threat gain.

    Steps:
    1. Commit: player assigns ready heroes and allies to the quest (exhausts them).
    2. Resolution: total willpower vs total staging threat.
       - willpower > threat  -> progress tokens added to active location or quest card
       - willpower < threat  -> player threat raised by the difference
       - willpower == threat -> nothing happens
    3. Quest advancement: if the current quest card is completed, move to the next one.
    """

    def execute(self):
        """Commit characters, resolve willpower vs. threat, and advance the quest if complete."""
        self._commit_to_quest()
        self._resolve_quest()
        self.table.questing.clear()

    # --- Commit step ---

    def _commit_to_quest(self) -> None:
        """Exhaust and register the characters chosen by _choose_questers."""
        characters = self._choose_questers(self._get_available_questers())
        for character in characters:
            character.exhaust()
            self.table.questing.append(character)

    def _get_available_questers(self) -> list[Hero | Ally]:
        """Return all ready heroes and board allies eligible to quest.

        Returns:
            list[Hero | Ally]: Characters that are not currently exhausted.
        """
        return [
            c for c in self.table.player_heroes + self.table.player_board
            if not c.exhausted
        ]

    def _choose_questers(self, available: list[Hero | Ally]) -> list[Hero | Ally]:
        """Delegates to the table's agent.

        Args:
            available (list[Hero | Ally]): Characters eligible to commit.

        Returns:
            list[Hero | Ally]: Characters that will quest this round.
        """
        return self.table.agent.choose_questing_characters(self.table, available)

    # --- Resolution step ---

    def _resolve_quest(self) -> None:
        """Compare total willpower against staging threat and apply the result."""
        willpower = sum(c.willpower for c in self.table.questing)
        threat = sum(card.threat for card in self.table.encounter_staging)
        net = willpower - threat

        if net > 0:
            self._add_progress(net)
        elif net < 0:
            self.table.table_threat += abs(net)

    def _add_progress(self, progress: int) -> None:
        """Distribute progress tokens, filling the active location first then the quest card.

        Args:
            progress (int): Total progress tokens to distribute.
        """
        if self.table.active_travel_location is not None:
            progress = self._progress_location(self.table.active_travel_location, progress)

        if progress > 0:
            self._progress_quest(progress)

    def _progress_location(self, location: Location, progress: int) -> int:
        """Add progress tokens to the active location and clear it if completed.

        Args:
            location (Location): The currently active travel location.
            progress (int): Progress tokens available to place.

        Returns:
            int: Leftover progress tokens after the location is filled (0 if not yet complete).
        """
        needed = location.required_progress - location.progress
        tokens = min(progress, needed)
        location.place_progress_token(tokens)

        if location.is_complete():
            self.table.active_travel_location = None
            self.table.encounter_discard.append(location)
            return progress - needed

        return 0

    def _progress_quest(self, progress: int) -> None:
        """Add progress tokens to the current quest card and advance the quest if completed.

        Args:
            progress (int): Number of progress tokens to place on the quest.
        """
        quest = self.table.get_current_quest()
        quest.place_progress_token(progress)

        if quest.progress >= quest.required_progress:
            self._advance_quest()

    def _advance_quest(self) -> None:
        """Remove the completed quest card; the next card in the deck becomes active."""
        self.table.quest_deck.pop(0)
