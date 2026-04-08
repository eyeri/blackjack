import pytest
from Game.card import Card
from Game.hand import Hand


def c(code: str) -> Card:
    new_card: Card = Card(rank=code[:-1], suit=code[-1])
    return new_card


def make_hand(*codes: str) -> Hand:
    new_hand: Hand = Hand()
    for code in codes:
        current_card: Card = c(code)
        new_hand.add(current_card)
    return new_hand


@pytest.mark.parametrize(
    "codes, expected_value",
    [
        (("10H", "7S"), 17),
        (("AH", "9S"), 20),
        (("AH", "AS"), 12),
        (("AH", "AS", "9D"), 21),
        (("AH", "AS", "9D", "9C"), 20),
        (("AH", "KS"), 21),
        (("AH", "9S", "AD"), 21),
        (("AH", "9S", "9D"), 19),
        (("KH", "QS", "2D"), 22),
        (("AH", "AS", "AD", "8C"), 21),
    ],
)
def test_best_total_cases(codes: tuple[str, ...], expected_value: int):
    new_hand: Hand = make_hand(*codes)
    assert new_hand.best_total() == expected_value


def test_blackjack_true_for_ace_plus_ten():
    new_hand: Hand = make_hand("AH", "KS")
    assert new_hand.is_blackjack() is True


def test_blackjack_false_for_three_card_21():
    new_hand: Hand = make_hand("7H", "7S", "7D")
    assert new_hand.is_blackjack() is False


def test_is_bust_true():
    new_hand: Hand = make_hand("KH", "QS", "2D")
    assert new_hand.is_bust() is True


def test_is_bust_false():
    new_hand: Hand = make_hand("AH", "9S")
    assert new_hand.is_bust() is False