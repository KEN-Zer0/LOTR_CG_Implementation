from .phase import Phase
from src.cards import Hero, Location


class TravelPhase(Phase):
    """
    Travel phase — player may move one location from the staging area
    to become the active travel location.

    Rules:
    - Travel is only possible when there is no active location.
    - Only locations in the staging area are eligible.
    - Some locations have a travel_cost requiring heroes to be exhausted.
    - The player may choose to pass and travel to nothing.
    """

    def execute(self):
        """Skip if a location is already active; otherwise let the player travel to one location."""
        if self.table.active_travel_location is not None:
            return

        eligible = self._get_eligible_locations()
        if not eligible:
            return

        location = self._choose_location(eligible)
        if location is None:
            return

        self._travel_to(location)

    # --- Location selection ---

    def _get_eligible_locations(self) -> list[Location]:
        """Return locations in the staging area whose travel cost can be paid.

        Returns:
            list[Location]: Affordable locations from the staging area.
        """
        return [
            card for card in self.table.encounter_staging
            if isinstance(card, Location) and self._can_afford_travel(card)
        ]

    def _can_afford_travel(self, location: Location) -> bool:
        """Check whether enough ready heroes are available to pay the travel cost.

        Args:
            location (Location): The location whose travel cost is being evaluated.

        Returns:
            bool: True if the travel cost can be paid with currently ready heroes.
        """
        cost = getattr(location, "travel_cost", 0)
        if cost == 0:
            return True
        ready_heroes = [h for h in self.table.player_heroes if not h.exhausted]
        return len(ready_heroes) >= cost

    def _choose_location(self, eligible: list[Location]) -> Location | None:
        """Select a location to travel to from the eligible list.

        Override this method to implement custom selection logic (e.g. for an AI agent).
        Return None to pass and skip travel this round.

        Args:
            eligible (list[Location]): Locations that can be travelled to this round.

        Returns:
            Location | None: The chosen location, or None to pass.
        """
        return max(eligible, key=lambda loc: loc.threat)

    # --- Travel execution ---

    def _travel_to(self, location: Location) -> None:
        """Pay the travel cost, remove the location from staging, and set it as active.

        Args:
            location (Location): The location to travel to.
        """
        cost = getattr(location, "travel_cost", 0)
        if cost > 0:
            self._pay_travel_cost(cost)

        self.table.encounter_staging.remove(location)
        self.table.active_travel_location = location

    def _pay_travel_cost(self, cost: int) -> None:
        """Exhaust the required number of ready heroes to pay the travel cost.

        Args:
            cost (int): Number of heroes that must be exhausted.
        """
        ready_heroes = [h for h in self.table.player_heroes if not h.exhausted]
        for hero in ready_heroes[:cost]:
            hero.exhaust()
