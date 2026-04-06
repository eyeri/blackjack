import pytest
from Game.card import Card
from Game.hand import Hand


def c(code: str) -> Card:
    # TODO:
    # - Convert a card code string into a Card object.
    # - Keep the same rank/suit split convention as the original test helper.
    pass



def make_hand(*codes: str) -> Hand:
    # TODO:
    # - Create an empty Hand.
    # - Convert each incoming code to a Card.
    # - Add each Card to the Hand in order.
    # - Return the completed Hand.
    pass


# TODO:
# - Restore the parametrize decorator for multiple Ace / total scenarios.
# - Reinsert the original (codes, expected) cases here.
def test_best_total_cases():
    # TODO:
    # - Build a hand from test input.
    # - Assert that best_total() matches the expected value.
    pass



def test_blackjack_true_for_ace_plus_ten():
    # TODO:
    # - Build a 2-card blackjack hand.
    # - Assert that is_blackjack() is True.
    pass



def test_blackjack_false_for_three_card_21():
    # TODO:
    # - Build a 3-card hand totaling 21.
    # - Assert that is_blackjack() is False.
    pass



def test_is_bust_true():
    # TODO:
    # - Build a hand whose total exceeds 21.
    # - Assert that is_bust() is True.
    pass



def test_is_bust_false():
    # TODO:
    # - Build a hand whose total does not exceed 21.
    # - Assert that is_bust() is False.
    pass
