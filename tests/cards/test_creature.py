import pytest
from src.cards.creatures import Creature
from config.cards_dict import Enemys


def test_creature_initialization():
    orc = Creature(Enemys.Dol_Guldur_Orcs, 1, 2, 3)

    assert orc.name == Enemys.Dol_Guldur_Orcs
    assert orc.attack == 1
    assert orc.defense == 2
    assert orc.hit_points == 3


def test_change_hit_points_reduces_hp():
    orc = Creature(Enemys.Dol_Guldur_Orcs, 1, 2, 3)

    orc.change_hp(-3)

    assert orc.hit_points == 0


def test_change_hit_points_increases_hp():
    orc = Creature(Enemys.Dol_Guldur_Orcs, 1, 2, 3)

    orc.change_hp(2)

    assert orc.hit_points == orc.max_hit_points


def test_multiple_hp_changes():
    orc = Creature(Enemys.Dol_Guldur_Orcs, 1, 2, 10)

    orc.change_hp(-3)
    orc.change_hp(-2)
    orc.change_hp(1)

    assert orc.hit_points == 6