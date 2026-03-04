import pytest
from .card import Card
from .hand import Hand

def test_ace_handling():
    hand = Hand()
    hand.add(Card("A", "S"))
    hand.add(Card("A", "H"))
    hand.add(Card("9", "D"))
    # A(11) + A(11) + 9 = 31 -> Ace 하나를 1로 변경 -> 21
    assert hand.best_total() == 21

def test_blackjack():
    hand = Hand()
    hand.add(Card("A", "S"))
    hand.add(Card("10", "H"))
    assert hand.is_blackjack() is True