from src.cards import BaseCard


def test_card_name():
    gandalf = BaseCard('Gandalf')
    thorn = BaseCard('Thorn')

    assert gandalf.name == 'Gandalf'
    assert thorn.name == 'Thorn'