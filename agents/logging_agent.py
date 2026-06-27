from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from agents.base_agent import BaseAgent
from src.logging.logger import Logger

if TYPE_CHECKING:
    from src.table import Table
    from src.cards import Hero, Ally, Enemy, Location


def _name(card: object) -> str:
    n = card.name
    return n.name if hasattr(n, "name") else str(n)


def _sphere_tokens(game_state: Table) -> str:
    pools: dict[str, int] = defaultdict(int)
    for h in game_state.player_heroes:
        pools[_name(h.sphere_of_influence)] += h.resource_pool
    return "  ".join(f"{sphere}: {count}" for sphere, count in pools.items())


class LoggingAgent(BaseAgent):
    """Wraps any BaseAgent and logs every decision through Logger."""

    def __init__(self, agent: BaseAgent) -> None:
        self._agent = agent

    def choose_questing_characters(
        self, game_state: Table, available: list[Hero | Ally]
    ) -> list[Hero | Ally]:
        chosen = self._agent.choose_questing_characters(game_state, available)
        names = [_name(c) for c in chosen]
        Logger.log(f"(Agent) [questers ({len(chosen)}/{len(available)}): {names or '—'}]")
        return chosen

    def choose_card_to_play(
        self, game_state: Table, playable: list[Ally]
    ) -> Ally | None:
        card = self._agent.choose_card_to_play(game_state, playable)
        tokens = _sphere_tokens(game_state)
        if card:
            Logger.log(f"(Agent) [played: {_name(card)} (cost {card.cost}) | {tokens}]")
        else:
            Logger.log(f"(Agent) [planning: pass | {tokens}]")
        return card

    def choose_location(
        self, game_state: Table, eligible: list[Location]
    ) -> Location | None:
        location = self._agent.choose_location(game_state, eligible)
        if location:
            Logger.log(f"(Agent) [travel to: {_name(location)} (threat {location.threat}, requires {location.required_progress} progress)]")
        else:
            Logger.log(f"(Agent) [travel: pass]")
        return location

    def choose_optional_engagement(
        self, game_state: Table, available: list[Enemy]
    ) -> list[Enemy]:
        chosen = self._agent.choose_optional_engagement(game_state, available)
        if chosen:
            Logger.log(f"(Agent) [optional engagement: {[_name(e) for e in chosen]}]")
        return chosen

    def choose_defender(
        self, game_state: Table, enemy: Enemy, available: list[Hero | Ally]
    ) -> Hero | Ally | None:
        defender = self._agent.choose_defender(game_state, enemy, available)
        if defender:
            dmg = max(0, enemy.attack - defender.defense)
            Logger.log(f"(Agent) [{_name(enemy)} (atk {enemy.attack}) attacks — defender: {_name(defender)} (def {defender.defense}, hp {defender.hit_points}) -> damage: {dmg}]")
        else:
            Logger.log(f"(Agent) [{_name(enemy)} (atk {enemy.attack}) attacks — undefended]")
        return defender

    def choose_undefended_target(
        self, game_state: Table, enemy: Enemy
    ) -> Hero:
        hero = self._agent.choose_undefended_target(game_state, enemy)
        Logger.log(f"(Agent) [undefended attack target: {_name(hero)} (hp {hero.hit_points})]")
        return hero

    def choose_attackers(
        self, game_state: Table, enemy: Enemy, available: list[Hero | Ally]
    ) -> list[Hero | Ally]:
        attackers = self._agent.choose_attackers(game_state, enemy, available)
        if attackers:
            total_atk = sum(a.attack for a in attackers)
            dmg = max(0, total_atk - enemy.defense)
            Logger.log(
                f"(Agent) [attack on {_name(enemy)} (def {enemy.defense}, hp {enemy.hit_points})"
                f" — attackers: {[_name(a) for a in attackers]}"
                f" (total atk {total_atk} -> damage: {dmg})]"
            )
        else:
            Logger.log(f"(Agent) [no attack on {_name(enemy)}]")
        return attackers
