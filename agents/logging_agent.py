from __future__ import annotations

from typing import TYPE_CHECKING

from agents.base_agent import BaseAgent
from logger import Logger

if TYPE_CHECKING:
    from src.table import Table
    from src.cards import Hero, Ally, Enemy, Location


def _name(card) -> str:
    n = card.name
    return n.name if hasattr(n, "name") else str(n)


class LoggingAgent(BaseAgent):
    """Wraps any BaseAgent and logs every decision through Logger."""

    def __init__(self, agent: BaseAgent) -> None:
        self._agent = agent

    def choose_questing_characters(
        self, game_state: Table, available: list[Hero | Ally]
    ) -> list[Hero | Ally]:
        chosen = self._agent.choose_questing_characters(game_state, available)
        names = [_name(c) for c in chosen]
        Logger.log(f"    questers ({len(chosen)}/{len(available)}): {names or '—'}")
        return chosen

    def choose_card_to_play(
        self, game_state: Table, playable: list[Ally]
    ) -> Ally | None:
        card = self._agent.choose_card_to_play(game_state, playable)
        if card:
            resources = sum(h.resource_pool for h in game_state.player_heroes)
            Logger.log(f"    zagrano: {_name(card)} (koszt {card.cost}, zasoby {resources})")
        else:
            Logger.log(f"    planning: pass")
        return card

    def choose_location(
        self, game_state: Table, eligible: list[Location]
    ) -> Location | None:
        location = self._agent.choose_location(game_state, eligible)
        if location:
            Logger.log(f"    podróż do: {_name(location)} (threat {location.threat}, potrzeba {location.required_progress} postępu)")
        else:
            Logger.log(f"    podróż: pass")
        return location

    def choose_optional_engagement(
        self, game_state: Table, available: list[Enemy]
    ) -> list[Enemy]:
        chosen = self._agent.choose_optional_engagement(game_state, available)
        if chosen:
            Logger.log(f"    opcjonalne zaangażowanie: {[_name(e) for e in chosen]}")
        return chosen

    def choose_defender(
        self, game_state: Table, enemy: Enemy, available: list[Hero | Ally]
    ) -> Hero | Ally | None:
        defender = self._agent.choose_defender(game_state, enemy, available)
        if defender:
            dmg = max(0, enemy.attack - defender.defense)
            Logger.log(f"    {_name(enemy)} (atk {enemy.attack}) atakuje — obrońca: {_name(defender)} (def {defender.defense}, hp {defender.hit_points}) → obrażenia: {dmg}")
        else:
            Logger.log(f"    {_name(enemy)} (atk {enemy.attack}) atakuje — atak niezablokowany")
        return defender

    def choose_undefended_target(
        self, game_state: Table, enemy: Enemy
    ) -> Hero:
        hero = self._agent.choose_undefended_target(game_state, enemy)
        Logger.log(f"    cel niezablokowanego ataku: {_name(hero)} (hp {hero.hit_points})")
        return hero

    def choose_attackers(
        self, game_state: Table, enemy: Enemy, available: list[Hero | Ally]
    ) -> list[Hero | Ally]:
        attackers = self._agent.choose_attackers(game_state, enemy, available)
        if attackers:
            total_atk = sum(a.attack for a in attackers)
            dmg = max(0, total_atk - enemy.defense)
            Logger.log(
                f"    atak na {_name(enemy)} (def {enemy.defense}, hp {enemy.hit_points})"
                f" — atakują: {[_name(a) for a in attackers]}"
                f" (Σatk {total_atk} → obrażenia: {dmg})"
            )
        else:
            Logger.log(f"    brak ataku na {_name(enemy)}")
        return attackers
