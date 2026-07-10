from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.table import Table
    from src.cards import Hero, Ally, Enemy, Location


class BaseAgent(ABC):
    """Strategy interface: the game engine calls these methods at each decision point.

    Implement all abstract methods to plug any agent (AI or human controller)
    into the game without changing the engine.
    """

    @abstractmethod
    def choose_questing_characters(
        self, game_state: Table, available: list[Hero | Ally]
    ) -> list[Hero | Ally]:
        """Return which characters commit to the quest this round.

        Args:
            game_state: Current shared table state.
            available: Characters that are ready (not exhausted).

        Returns:
            Subset of available to send on the quest.
        """

    @abstractmethod
    def choose_card_to_play(
        self, game_state: Table, playable: list[Ally]
    ) -> Ally | None:
        """Return a card to play from hand, or None to pass.

        Args:
            game_state: Current shared table state.
            playable: Ally cards in hand whose cost can be paid.

        Returns:
            The card to play, or None to end the planning phase early.
        """

    @abstractmethod
    def choose_location(
        self, game_state: Table, eligible: list[Location]
    ) -> Location | None:
        """Return a location to travel to, or None to skip travel.

        Args:
            game_state: Current shared table state.
            eligible: Locations in the staging area whose cost can be paid.

        Returns:
            The location to travel to, or None to pass.
        """

    @abstractmethod
    def choose_optional_engagement(
        self, game_state: Table, available: list[Enemy]
    ) -> list[Enemy]:
        """Return enemies to voluntarily engage from the staging area.

        Args:
            game_state: Current shared table state.
            available: Enemies currently in the staging area.

        Returns:
            Enemies to engage (may be empty).
        """

    @abstractmethod
    def choose_defender(
        self, game_state: Table, enemy: Enemy, available: list[Hero | Ally]
    ) -> Hero | Ally | None:
        """Return a defender for the enemy's attack, or None for an undefended attack.

        Args:
            game_state: Current shared table state.
            enemy: The enemy that is attacking.
            available: Characters that are ready.

        Returns:
            The chosen defender, or None to leave the attack undefended.
        """

    @abstractmethod
    def choose_undefended_target(
        self, game_state: Table, enemy: Enemy
    ) -> Hero:
        """Return the hero who absorbs an undefended attack.

        Args:
            game_state: Current shared table state.
            enemy: The attacking enemy.

        Returns:
            The hero who will take the full damage.
        """

    @abstractmethod
    def choose_attackers(
        self, game_state: Table, enemy: Enemy, available: list[Hero | Ally]
    ) -> list[Hero | Ally]:
        """Return characters that will attack the given enemy.

        Args:
            game_state: Current shared table state.
            enemy: The enemy being attacked.
            available: Characters that are ready.

        Returns:
            Characters committed to this attack (empty to skip).
        """

    def on_defense_resolved(
        self, enemy: Enemy, defender: Hero | Ally, damage: int
    ) -> None:
        """Called after a defended enemy attack is resolved. Override to observe results."""

    def on_undefended_resolved(
        self, enemy: Enemy, hero: Hero, damage: int
    ) -> None:
        """Called after an undefended enemy attack is resolved. Override to observe results."""

    def on_attack_resolved(
        self, enemy: Enemy, attackers: list[Hero | Ally], damage: int, killed: bool
    ) -> None:
        """Called after the player's attack against an enemy is resolved. Override to observe results."""

    def on_no_heroes_for_undefended(self, enemy: Enemy) -> None:
        """Called when an undefended attack has no heroes to target. Override to observe."""
