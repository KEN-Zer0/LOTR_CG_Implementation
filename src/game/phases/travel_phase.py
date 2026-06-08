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
        """Returns locations in the staging area whose travel cost can be paid."""
        return [
            card for card in self.table.encounter_staging
            if isinstance(card, Location) and self._can_afford_travel(card)
        ]

    def _can_afford_travel(self, location: Location) -> bool:
        """Returns True if enough ready heroes are available to pay the travel cost."""
        cost = getattr(location, "travel_cost", 0)
        if cost == 0:
            return True
        ready_heroes = [h for h in self.table.player_heroes if not h.exhausted]
        return len(ready_heroes) >= cost

    def _choose_location(self, eligible: list[Location]) -> Location | None:
        """
        Selects a location to travel to from the eligible list.

        Override this method to implement custom selection logic,
        e.g. for an AI agent. Returns None to pass.
        Default: travels to the highest-threat location, removing the most
        staging pressure while it is being cleared.
        """
        return max(eligible, key=lambda loc: loc.threat)

    # --- Travel execution ---

    def _travel_to(self, location: Location) -> None:
        """Pays the travel cost, removes the location from staging, sets it as active."""
        cost = getattr(location, "travel_cost", 0)
        if cost > 0:
            self._pay_travel_cost(cost)

        self.table.encounter_staging.remove(location)
        self.table.active_travel_location = location

    def _pay_travel_cost(self, cost: int) -> None:
        """Exhausts the required number of ready heroes to pay the travel cost."""
        ready_heroes = [h for h in self.table.player_heroes if not h.exhausted]
        for hero in ready_heroes[:cost]:
            hero.exhaust()
