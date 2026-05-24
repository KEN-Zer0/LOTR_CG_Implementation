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
        defender = self._choose_defender(enemy)

        if defender is not None:
            self._resolve_defended_attack(enemy, defender)
        else:
            hero = self._choose_undefended_target(enemy)
            self._resolve_undefended_attack(enemy, hero)

    def _resolve_defended_attack(self, enemy: Enemy, defender: Hero | Ally) -> None:
        """Exhausts the defender and applies reduced damage."""
        defender.exhaust()
        self.table.defending.append(defender)

        damage = max(0, enemy.attack - defender.defense)
        if damage > 0:
            defender.take_damage(damage)
            if defender.is_dead() and isinstance(defender, Ally):
                self.table.player_board.remove(defender)

    def _resolve_undefended_attack(self, enemy: Enemy, hero: Hero) -> None:
        """Deals full unblocked enemy attack directly to a hero."""
        hero.change_hp(-enemy.attack)

    # --- Defender selection ---

    def _choose_defender(self, enemy: Enemy) -> Hero | Ally | None:
        """
        Selects a defender for the given enemy attack.

        Override this method to implement custom selection logic,
        e.g. for an AI agent. Return None to leave the attack undefended.
        Default: the ready character with the highest defense value.
        """
        ready = self._get_ready_characters()
        if not ready:
            return None
        return max(ready, key=lambda c: c.defense)

    def _choose_undefended_target(self, enemy: Enemy) -> Hero:
        """
        Selects a hero to receive an undefended attack.

        Override this method to implement custom selection logic,
        e.g. for an AI agent.
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
        attackers = self._choose_attackers(enemy)
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

    # --- Attacker selection ---

    def _choose_attackers(self, enemy: Enemy) -> list[Hero | Ally]:
        """
        Selects characters that will attack the given enemy.

        Override this method to implement custom selection logic,
        e.g. for an AI agent. Return an empty list to skip attacking.
        Default: all ready characters attack together.
        """
        return self._get_ready_characters()

    # ==========================================================================
    # Helpers
    # ==========================================================================

    def _get_ready_characters(self) -> list[Hero | Ally]:
        """Returns all non-exhausted heroes and board allies."""
        return [
            c for c in self.table.player_heroes + self.table.player_board
            if not c.exhausted
        ]