from src.cards import BaseCard
from config import *


def test_card_name():
    gandalf = BaseCard(Allies.Gandalf)
    eleanor = BaseCard(Heroes.Eleanor)

    assert Allies_dict[gandalf.name] == 'Gandalf'
    assert Allies_dict[eleanor.name] == 'Eleanor'