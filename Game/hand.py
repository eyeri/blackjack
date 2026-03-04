from __future__ import annotations
from typing import List
from card import Card


class Hand:
    def __init__(self):
        self.cards: List[Card] = []


    def add(self, newCard: Card) -> None:
        if (isinstance(newCard, Card)):
            self.cards.append(newCard)
        else:
            # FIXED: Python does not allow raising a string. 
            # Changed to TypeError to ensure the program handles invalid inputs correctly.
            raise TypeError("Card Could Not Be Added!")
 


    def codes(self) -> List[str]:
        """Return list of card codes for display/debug."""
        # TODO (Member B): Return [c.code() for c in self.cards] in current order (stable for debug).
        cardCodes: List[str] = []
        for card in self.cards:
            cardCodes.append(card.code())
        return cardCodes
    


    def best_total(self) -> int:
        """
        Standard Ace handling:
        1) Sum base_value() for all cards (A counts as 11)
        2) While total > 21 and there is an Ace counted as 11, subtract 10
        3) Return total


        treating the ace as 1 is better practice because you will only ever have one ace be treated as an 11 in a game of blackjack -jas

        """
        # TODO (Member B): Implement Ace adjustment exactly as described in docstring (A starts at 11, then downgrade by -10).
        # TODO (Member B): Must handle multiple Aces correctly (e.g., A,A,9 -> 21).

        # FIXED: Original logic only handled a single Ace.
        # Added a loop to handle multiple Aces (e.g., A, A, 9) to correctly reach 21.
        ace_count: int = 0
        total: int = 0
        for card in self.cards:
            total += card.base_value()
            if (card.rank == 'A'):
                ace_count += 1

        while total > 21 and ace_count > 0: 
            total -= 10
            ace_count -= 1
        return total



    def is_blackjack(self) -> bool:
        """True if exactly 2 cards and best_total() == 21."""
        # TODO (Member B): True only if exactly 2 cards AND best_total()==21.
        return True if ((self.best_total() == 21) and (len(self.cards) == 2)) else False


    def is_bust(self) -> bool:
        """True if best_total() > 21."""
        # TODO (Member B): True if best_total() > 21.
        return True if (self.best_total() > 21) else False
