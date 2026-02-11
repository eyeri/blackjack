from __future__ import annotations
from typing import List
from card import Card


class Hand:
    def __init__(self):
        self.cards: List[Card] = []
    pass 

    def add(self, card: Card) -> None:
        """Add a card to the hand."""
        # TODO (Member B): Append card to self.cards (preserve draw order).
    pass

    def codes(self) -> List[str]:
        """Return list of card codes for display/debug."""
        # TODO (Member B): Return [c.code() for c in self.cards] in current order (stable for debug). test edit
    pass

    def best_total(self) -> int:
        """
        Standard Ace handling:
        1) Sum base_value() for all cards (A counts as 11)
        2) While total > 21 and there is an Ace counted as 11, subtract 10
        3) Return total
        """
        # TODO (Member B): Implement Ace adjustment exactly as described in docstring (A starts at 11, then downgrade by -10).

        # TODO (Member B): Must handle multiple Aces correctly (e.g., A,A,9 -> 21).
    pass

    def is_blackjack(self) -> bool:
        """True if exactly 2 cards and best_total() == 21."""
        # TODO (Member B): True only if exactly 2 cards AND best_total()==21.
    pass

    def is_bust(self) -> bool:
        """True if best_total() > 21."""
        # TODO (Member B): True if best_total() > 21.
    pass
