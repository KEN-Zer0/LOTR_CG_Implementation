import pytest
from src.cards.creatures import Creature
from config.cards_dict import Enemys


def test_creature_initialization():
    orc = Creature(Enemys.Dol_Guldur_Orcs, 1, 2, 3, 3)

    assert orc.name == Enemys.Dol_Guldur_Orcs
    assert orc.attack == 1
    assert orc.defense == 2
    assert orc.hitPoints == 3


def test_change_hit_points_reduces_hp():
    orc = Creature(Enemys.Dol_Guldur_Orcs, 1, 2, 3, 3)

    orc.changeHitPoints(-3)

    assert orc.hitPoints == 0


def test_change_hit_points_increases_hp():
    orc = Creature(Enemys.Dol_Guldur_Orcs, 1, 2, 3, 3)

    orc.changeHitPoints(2)

    assert orc.hitPoints == 5


def test_multiple_hp_changes():
    orc = Creature(Enemys.Dol_Guldur_Orcs, 1, 2, 10, 10)

    orc.changeHitPoints(-3)
    orc.changeHitPoints(-2)
    orc.changeHitPoints(1)

    assert orc.hitPoints == 6