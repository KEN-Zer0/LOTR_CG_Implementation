"""Alpha/Beta minimax agent for Lord of the Rings: The Card Game."""
from __future__ import annotations

from itertools import chain, combinations
from math import inf
from typing import TYPE_CHECKING

from agents.base_agent import BaseAgent

if TYPE_CHECKING:
    from src.table import Table
    from src.cards import Hero, Ally, Enemy, Location


def _power_set(lst: list) -> chain:
    return chain.from_iterable(combinations(lst, r) for r in range(len(lst) + 1))


class AlphaBetaAgent(BaseAgent):
    """Two-ply minimax agent with alpha-beta pruning.

    Player decisions are MAX nodes; encounter reveals are MIN nodes.
    The questing phase enumerates all 2^N character subsets (MAX) and for
    each subset finds the worst-case encounter reveal (MIN) with alpha cutoff.
    All other decision points use direct heuristic evaluation.
    """

    # ── Position evaluator ───────────────────────────────────────────────────

    def _evaluate(self, state: Table) -> float:
        if state.check_win_condition():
            return 10_000.0
        if state.check_lose_condition():
            return -10_000.0

        score = 0.0

        quest = state.get_current_quest()
        if quest:
            score += quest.progress * 8.0
            score -= (quest.required_progress - quest.progress) * 1.5

        score -= state.table_threat * 2.5
        margin = 50 - state.table_threat
        if margin <= 6:
            score -= (7 - margin) ** 2 * 5.0

        for hero in state.player_heroes:
            score += hero.hit_points * 5.0
        for ally in state.player_board:
            score += (ally.attack + ally.defense + ally.willpower) * 2.0

        score += len(state.player_hand) * 1.0

        for enemy in state.encounter_engagement:
            score -= enemy.attack * 2.5 + enemy.hit_points * 1.5
        for card in state.encounter_staging:
            score -= card.threat * 2.0

        for hero in state.player_heroes:
            score += hero.resource_pool * 0.5

        return score

    # ── Questing: 2-ply alpha-beta minimax ──────────────────────────────────

    def choose_questing_characters(
        self, game_state: Table, available: list
    ) -> list:
        staging_threat = sum(c.threat for c in game_state.encounter_staging)
        base_score = self._evaluate(game_state)
        # Most-dangerous cards first → MIN finds low beta sooner → more alpha cuts
        deck = sorted(game_state.encounter_deck, key=lambda c: self._card_danger(game_state, c))
        # Highest-willpower subsets first → alpha rises early → fewer MIN loops run to completion
        subsets = sorted(_power_set(available), key=lambda s: sum(c.willpower for c in s), reverse=True)

        alpha, best = -inf, []
        for subset in subsets:
            score = self._min_encounter(game_state, subset, staging_threat, alpha, base_score, deck)
            if score > alpha:
                alpha, best = score, list(subset)
        return best

    def _min_encounter(
        self, state: Table, questers: tuple, staging_threat: int,
        alpha: float, base_score: float, deck: list
    ) -> float:
        """MIN node: worst-case encounter reveal after questers commit."""
        quest_score = base_score + self._quest_delta(state, questers, staging_threat)
        if not deck:
            return quest_score
        qnames = {c.name for c in questers}
        fighters = [
            c for c in state.player_heroes + state.player_board
            if c.name not in qnames and not c.exhausted
        ]
        beta = inf
        for card in deck:
            score = quest_score + self._reveal_delta(state, card, fighters)
            if score < beta:
                beta = score
            if beta <= alpha:
                return beta
        return beta

    def _card_danger(self, state: Table, card) -> float:
        """Danger level of revealing this card; lower = more dangerous, so sort ascending."""
        is_enemy = hasattr(card, 'engagement')
        if is_enemy and card.engagement <= state.table_threat:
            return -(card.attack * 3.0 + card.hit_points)
        return -(card.threat * 2.0)

    def _reveal_delta(self, state: Table, card, fighters: list) -> float:
        """Score impact of revealing this encounter card.

        Enemies that auto-engage (engagement <= table_threat) are evaluated
        via combat estimate against remaining non-questing characters.
        All other cards contribute only their staging threat penalty.
        """
        is_enemy = hasattr(card, 'engagement')
        if not is_enemy or card.engagement > state.table_threat:
            return -(card.threat * 2.0)
        return self._combat_estimate(fighters, [card])

    def _quest_delta(
        self, state: Table, questers: tuple, staging_threat: int
    ) -> float:
        """Evaluation delta from committing these characters to the quest (no deepcopy)."""
        net = sum(c.willpower for c in questers) - staging_threat
        delta = 0.0

        if net > 0:
            delta += self._progress_gain(state, net)
        elif net < 0:
            new_threat = state.table_threat + abs(net)
            if new_threat >= 50:
                return -10_000.0
            delta += (state.table_threat - new_threat) * 2.5
            for t, sign in ((state.table_threat, +1), (new_threat, -1)):
                m = 50 - t
                if m <= 6:
                    delta += sign * (7 - m) ** 2 * 5.0

        if state.encounter_engagement:
            qnames = {c.name for c in questers}
            fighters = [
                c for c in state.player_heroes + state.player_board
                if c.name not in qnames and not c.exhausted
            ]
            delta += self._combat_estimate(fighters, state.encounter_engagement)

        return delta

    def _progress_gain(self, state: Table, tokens: int) -> float:
        """Estimate the evaluation gain from placing `tokens` progress tokens."""
        remaining = tokens
        delta = 0.0

        if state.active_travel_location is not None:
            loc = state.active_travel_location
            needed = loc.required_progress - loc.progress
            applied = min(remaining, needed)
            delta += applied * 3.0
            remaining -= applied
            if applied >= needed:
                delta += 5.0

        if remaining > 0 and state.quest_deck:
            quest = state.get_current_quest()
            needed = quest.required_progress - quest.progress
            applied = min(remaining, needed)
            delta += applied * 9.5
            if applied >= needed and len(state.quest_deck) == 1:
                return 10_000.0

        return delta

    def _combat_estimate(self, fighters: list, enemies: list) -> float:
        """Expected combat score with fighters against given enemies."""
        remaining_atk = sum(c.attack for c in fighters)
        defenders = sorted(fighters, key=lambda c: c.defense, reverse=True)
        enemies_sorted = sorted(enemies, key=lambda e: e.attack, reverse=True)

        score = 0.0
        for i, enemy in enumerate(enemies_sorted):
            best_def = defenders[i].defense if i < len(defenders) else 0
            score -= max(0, enemy.attack - best_def) * 1.5
            kill_cost = enemy.defense + enemy.hit_points
            if remaining_atk >= kill_cost:
                score += 4.0
                remaining_atk -= kill_cost

        return score

    # ── Planning ─────────────────────────────────────────────────────────────

    def choose_card_to_play(
        self, game_state: Table, playable: list
    ) -> Ally | None:
        if not playable:
            return None
        return max(playable, key=lambda a: (a.attack * 2 + a.defense + a.willpower) / max(a.cost, 1))

    # ── Travel ───────────────────────────────────────────────────────────────

    def choose_location(
        self, game_state: Table, eligible: list
    ) -> Location | None:
        if not eligible:
            return None
        return max(eligible, key=lambda loc: loc.threat)

    # ── Encounter ────────────────────────────────────────────────────────────

    def choose_optional_engagement(
        self, game_state: Table, available: list
    ) -> list:
        ready = [c for c in game_state.player_heroes + game_state.player_board if not c.exhausted]
        total_atk = sum(c.attack for c in ready)
        to_engage = []
        for enemy in sorted(available, key=lambda e: e.hit_points):
            if total_atk >= enemy.defense + enemy.hit_points:
                to_engage.append(enemy)
                total_atk = max(0, total_atk - (enemy.defense + enemy.hit_points))
        return to_engage

    # ── Combat ───────────────────────────────────────────────────────────────

    def choose_defender(
        self, game_state: Table, enemy, available: list
    ) -> Hero | Ally | None:
        if not available:
            return None

        best_score, best_defender = -inf, None
        for defender in available:
            dmg = max(0, enemy.attack - defender.defense)
            is_ally = hasattr(defender, 'cost')

            if dmg == 0:
                score = 50.0
            elif is_ally and dmg >= defender.hit_points:
                score = 10.0
            else:
                score = (defender.hit_points - dmg) * (1.5 if is_ally else 4.0)

            if score > best_score:
                best_score, best_defender = score, defender

        return best_defender

    def choose_undefended_target(
        self, game_state: Table, enemy
    ) -> Hero:
        return max(game_state.player_heroes, key=lambda h: h.hit_points)

    def choose_attackers(
        self, game_state: Table, enemy, available: list
    ) -> list:
        if not available:
            return []
        by_attack = sorted(available, key=lambda c: c.attack, reverse=True)
        chosen, total = [], 0
        for char in by_attack:
            chosen.append(char)
            total += char.attack
            if total - enemy.defense >= enemy.hit_points:
                return chosen
        return list(available)
