import pytest
from enum import Enum

from src.cards.base_card import BaseCard


# Set up a fake Enum for testing purposes
class CardName(Enum):
    TEST_CARD = "Test Card Name"


# Concrete implementation of ABC for testing
class ConcreteCard(BaseCard):
    pass


def test_base_card_initialization():
    # Check if name property returns the correct enum value
    card = ConcreteCard(CardName.TEST_CARD)
    assert card.name == CardName.TEST_CARD


@pytest.mark.parametrize(
    "empty_value",
    [
        None,
        "",
        [],
    ],
)
def test_base_card_empty_name(empty_value):
    # Check if empty or falsy values return "Name empty"
    card = ConcreteCard(empty_value)
    assert card.name == "Name empty"