import pytest
from src.game.phases.combat_phase import CombatPhase
from src.cards import Hero, Ally, Enemy
from config.limited.cards_list import Heroes, Allies, Enemies, Sphere
from config.limited.cards_registry import CARDS


@pytest.fixture
def weak_enemy():
    """Low-HP enemy (attack=2, defense=0, HP=3) that can be killed by the default party."""
    return Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2)


@pytest.fixture
def tank_enemy():
    """High-HP enemy that the default party cannot kill in one round."""
    return Enemy(Enemies.Ungoliants_Spawn, 5, 2, 100, 32, 3)


# ── Defender selection ─────────────────────────────────────────────────────

def test_choose_defender_picks_highest_defense(table):
    """Default defender is the ready character with the highest defense."""
    phase = CombatPhase(table)
    enemy = Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2)
    defender = phase._choose_defender(enemy, table.player_heroes)
    assert defender.defense == max(h.defense for h in table.player_heroes)


def test_choose_defender_returns_none_when_no_ready(table):
    """Returns None when the available pool is empty."""
    phase = CombatPhase(table)
    enemy = Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2)
    assert phase._choose_defender(enemy, []) is None


# ── Defended attacks ───────────────────────────────────────────────────────

def test_defended_attack_reduces_damage_by_defense(table, weak_enemy):
    """Defender absorbs enemy.attack - defender.defense damage."""
    phase = CombatPhase(table)
    # Eleanor: defense=2, weak_enemy: attack=2 → 0 damage
    eleanor = table.player_heroes[1]
    phase._resolve_defended_attack(weak_enemy, eleanor)
    assert eleanor.hit_points == eleanor.max_hit_points


def test_dead_ally_removed_from_board_after_defending(table):
    """Ally with 0 HP after defending is removed from the player board."""
    phase = CombatPhase(table)
    fragile = Ally(Allies.Gondorian_Spearman, 1, 0, 1, 0, Sphere.Tactics, 2)
    table.player_board.append(fragile)
    strong = Enemy(Enemies.Ungoliants_Spawn, 5, 2, 9, 32, 3)
    phase._resolve_defended_attack(strong, fragile)
    assert fragile not in table.player_board


def test_dead_hero_removed_from_heroes_after_defending(table):
    """Hero with 0 HP after defending is removed from player_heroes."""
    phase = CombatPhase(table)
    hero = table.player_heroes[0]
    hero._hit_points = 1
    strong = Enemy(Enemies.Ungoliants_Spawn, 5, 2, 9, 32, 3)
    phase._resolve_defended_attack(strong, hero)
    assert hero not in table.player_heroes


# ── Undefended attacks ─────────────────────────────────────────────────────

def test_undefended_attack_deals_full_enemy_attack(table):
    """Full enemy attack damage goes to the hero with the most HP when undefended."""
    phase = CombatPhase(table)
    enemy = Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2)
    table.encounter_engagement.append(enemy)
    for h in table.player_heroes:
        h.exhaust()
    hp_before = {h: h.hit_points for h in table.player_heroes}
    phase._enemy_attacks_phase()
    total_damage = sum(hp_before[h] - h.hit_points for h in table.player_heroes)
    assert total_damage == enemy.attack


def test_dead_hero_removed_on_undefended_attack(table):
    """Hero with 0 HP after an undefended attack is removed from player_heroes."""
    phase = CombatPhase(table)
    hero = Hero(Heroes.Eowyn, 1, 1, 1, 4, Sphere.Spirit, 9)  # 1 HP
    table.player_heroes = [hero]
    enemy = Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2)
    phase._resolve_undefended_attack(enemy, hero)
    assert hero not in table.player_heroes


def test_no_crash_when_all_heroes_gone_before_undefended(table):
    """No exception when player_heroes is empty at the start of an enemy attack."""
    phase = CombatPhase(table)
    table.player_heroes.clear()
    enemy = Enemy(Enemies.Dol_Guldur_Orcs, 2, 0, 3, 10, 2)
    phase._resolve_enemy_attack(enemy)  # must not raise


# ── Player attacks ─────────────────────────────────────────────────────────

def test_player_kills_enemy_removed_and_added_to_discard(table, weak_enemy):
    """Defeated enemy leaves encounter_engagement and enters encounter_discard."""
    phase = CombatPhase(table)
    table.encounter_engagement.append(weak_enemy)
    phase._player_attacks_phase()
    assert weak_enemy not in table.encounter_engagement
    assert weak_enemy in table.encounter_discard


def test_surviving_enemy_stays_in_engagement(table, tank_enemy):
    """Enemy that survives player attacks remains in encounter_engagement."""
    phase = CombatPhase(table)
    table.encounter_engagement.append(tank_enemy)
    phase._player_attacks_phase()
    assert tank_enemy in table.encounter_engagement


def test_choose_attackers_uses_minimum_to_kill(table, weak_enemy):
    """_choose_attackers picks the fewest characters needed for lethal damage."""
    phase = CombatPhase(table)
    # Thalin(atk=2) alone: 2 < 3 HP. Thalin+Eleanor(2+1=3): lethal → 2 attackers, not 3.
    attackers = phase._choose_attackers(weak_enemy, table.player_heroes)
    total = sum(a.attack for a in attackers)
    assert total - weak_enemy.defense >= weak_enemy.hit_points
    assert len(attackers) < len(table.player_heroes)


def test_choose_attackers_returns_all_when_cannot_kill(table, tank_enemy):
    """Falls back to all available characters when no subset can deal lethal damage."""
    phase = CombatPhase(table)
    attackers = phase._choose_attackers(tank_enemy, table.player_heroes)
    assert set(attackers) == set(table.player_heroes)


# ── Post-execute cleanup ───────────────────────────────────────────────────

def test_defending_and_attacking_cleared_after_execute(table, weak_enemy):
    """Both defending and attacking lists are empty after execute finishes."""
    phase = CombatPhase(table)
    table.encounter_engagement.append(weak_enemy)
    phase.execute()
    assert table.defending == []
    assert table.attacking == []


def test_two_enemies_first_killed_second_survives(table):
    """First enemy is killed; heroes are exhausted after so the second enemy survives."""
    phase = CombatPhase(table)
    easy = CARDS[Enemies.Black_Forest_Bats].copy()  # def=0, hp=2 — one attacker lethal
    tank = CARDS[Enemies.Ungoliants_Spawn].copy()   # def=2, hp=9 — survives
    table.encounter_engagement.extend([easy, tank])
    phase._player_attacks_phase()
    assert easy in table.encounter_discard
    assert tank in table.encounter_engagement


def test_two_enemies_both_attack_player(table):
    """Two engaged enemies each deal damage to the player's heroes."""
    phase = CombatPhase(table)
    orc1 = CARDS[Enemies.Dol_Guldur_Orcs].copy()
    orc2 = CARDS[Enemies.Dol_Guldur_Orcs].copy()
    table.encounter_engagement.extend([orc1, orc2])
    for h in table.player_heroes:
        h.exhaust()
    hp_before = sum(h.hit_points for h in table.player_heroes)
    phase._enemy_attacks_phase()
    hp_after = sum(h.hit_points for h in table.player_heroes)
    assert hp_after < hp_before
