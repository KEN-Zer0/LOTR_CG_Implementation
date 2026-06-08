from .phase import Phase
from src.cards import Hero, Ally, Enemy


class CombatPhase(Phase):
    """
    Combat phase — enemies attack, then the player attacks enemies.

    Steps:
    1. Enemy attacks: each enemy in encounter_engagement attacks the player.
       - Player declares a defender (exhausted) or takes the attack undefended.
       - Defended: damage = max(0, enemy.attack - defender.defense)
       - Undefended: full enemy.attack dealt directly to a chosen hero.
    2. Player attacks: player may attack each enemy in encounter_engagement.
       - Player declares one or more attackers (exhausted).
       - Damage = max(0, sum of attacker.attack - enemy.defense)
       - Enemies reduced to 0 hit points are defeated and removed.

    All _choose_* methods receive the current available pool explicitly so that
    subclasses (e.g. AI agents) do not need to replicate the ready-character query.
    """

    def execute(self):
        self._enemy_attacks_phase()
        self._player_attacks_phase()
        self.table.defending.clear()
        self.table.attacking.clear()

    # ==========================================================================
    # Enemy attacks
    # ==========================================================================

    def _enemy_attacks_phase(self) -> None:
        """Processes one attack from each engaged enemy."""
        for enemy in list(self.table.encounter_engagement):
            self._resolve_enemy_attack(enemy)

    def _resolve_enemy_attack(self, enemy: Enemy) -> None:
        """Resolves a single enemy attack: defender declaration then damage."""
        available = self._get_ready_characters()
        defender = self._choose_defender(enemy, available)

        if defender is not None:
            self._resolve_defended_attack(enemy, defender)
        else:
            if not self.table.player_heroes:
                return
            hero = self._choose_undefended_target(enemy)
            self._resolve_undefended_attack(enemy, hero)

    def _resolve_defended_attack(self, enemy: Enemy, defender: Hero | Ally) -> None:
        """Exhausts the defender and applies reduced damage."""
        defender.exhaust()
        self.table.defending.append(defender)

        damage = max(0, enemy.attack - defender.defense)
        if damage > 0:
            defender.take_damage(damage)
            if defender.is_dead():
                if isinstance(defender, Ally):
                    self.table.player_board.remove(defender)
                else:
                    self.table.player_heroes.remove(defender)

    def _resolve_undefended_attack(self, enemy: Enemy, hero: Hero) -> None:
        """Deals full unblocked enemy attack directly to a hero."""
        hero.take_damage(enemy.attack)
        if hero.is_dead():
            self.table.player_heroes.remove(hero)

    # --- Defender selection ---

    def _choose_defender(self, enemy: Enemy, available: list[Hero | Ally]) -> Hero | Ally | None:
        """
        Selects a defender for the given enemy attack.

        Override for custom logic. Return None to leave the attack undefended.
        Default: the ready character with the highest defense value.
        """
        if not available:
            return None
        return max(available, key=lambda c: c.defense)

    def _choose_undefended_target(self, enemy: Enemy) -> Hero:
        """
        Selects a hero to receive an undefended attack.

        Override for custom logic.
        Default: the hero with the most remaining hit points.
        """
        return max(self.table.player_heroes, key=lambda h: h.hit_points)

    # ==========================================================================
    # Player attacks
    # ==========================================================================

    def _player_attacks_phase(self) -> None:
        """Gives the player one attack opportunity against each engaged enemy."""
        for enemy in list(self.table.encounter_engagement):
            self._resolve_player_attack(enemy)

    def _resolve_player_attack(self, enemy: Enemy) -> None:
        """Resolves a single player attack: attacker declaration then damage."""
        available = self._get_ready_characters()
        attackers = self._choose_attackers(enemy, available)
        if not attackers:
            return

        for attacker in attackers:
            attacker.exhaust()
            self.table.attacking.append(attacker)

        damage = max(0, sum(a.attack for a in attackers) - enemy.defense)
        if damage > 0:
            enemy.take_damage(damage)

        if enemy.is_dead():
            self.table.encounter_engagement.remove(enemy)
            self.table.encounter_discard.append(enemy)

    # --- Attacker selection ---

    def _choose_attackers(self, enemy: Enemy, available: list[Hero | Ally]) -> list[Hero | Ally]:
        """
        Selects characters that will attack the given enemy.

        Override for custom logic. Return an empty list to skip attacking.
        Default: commits the minimum set of attackers (strongest first) sufficient
        to deal lethal damage, preserving the rest for subsequent enemies.
        Falls back to all available if the enemy cannot be killed regardless.
        """
        if not available:
            return []

        by_attack = sorted(available, key=lambda c: c.attack, reverse=True)
        chosen, total = [], 0
        for char in by_attack:
            chosen.append(char)
            total += char.attack
            if total - enemy.defense >= enemy.hit_points:
                return chosen

        return available

    # ==========================================================================
    # Helpers
    # ==========================================================================

    def _get_ready_characters(self) -> list[Hero | Ally]:
        """Returns all non-exhausted heroes and board allies."""
        return [
            c for c in self.table.player_heroes + self.table.player_board
            if not c.exhausted
        ]
