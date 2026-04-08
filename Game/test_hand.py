import pytest
from Game.card import Card
from Game.hand import Hand


def c(code: str) -> Card:
    # TODO:
    # - Convert a card code string into a Card object.
    new_card: Card = Card(rank=str[:-1], suit=str[-1])
    # - Keep the same rank/suit split convention as the original test helper.
    return new_card



def make_hand(*codes: str) -> Hand:
    # TODO:
    # - Create an empty Hand.
    new_hand: Hand = Hand()
    # - Convert each incoming code to a Card.
    for code in codes:
        current_card: Card = c(code)
        new_hand.add(current_card)
    # - Add each Card to the Hand in order.
    # - Return the completed Hand.
    return new_hand


# TODO:
# - Restore the parametrize decorator for multiple Ace / total scenarios.
# - Reinsert the original (codes, expected) cases here.
def test_best_total_cases(*codes: str, expected_value: int):
    # TODO:
    # - Build a hand from test input.
    new_hand: Hand = make_hand(codes)
    # - Assert that best_total() matches the expected value.
    assert new_hand.best_total() == expected_value



def test_blackjack_true_for_ace_plus_ten():
    # TODO:
    # - Build a 2-card blackjack hand.
    new_hand: Hand = make_hand(["10D","AS"])
    # - Assert that is_blackjack() is True.
    assert new_hand.is_blackjack()



def test_blackjack_false_for_three_card_21():
    # TODO:
    # - Build a 3-card hand totaling 21.
    new_hand: Hand = make_hand(["10H","10D","AS"])
    # - Assert that is_blackjack() is False.
    assert not new_hand.is_blackjack()



def test_is_bust_true():
    # TODO:
    # - Build a hand whose total exceeds 21.
    new_hand: Hand = make_hand(["10H","10D","10S"])
    # - Assert that is_bust() is True.
    assert new_hand.is_bust()




def test_is_bust_false():
    # TODO:
    # - Build a hand whose total does not exceed 21.
    new_hand: Hand = make_hand(["10H","10D"])
    # - Assert that is_bust() is False.
    assert not new_hand.is_bust()
