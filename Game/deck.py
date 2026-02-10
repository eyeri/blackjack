from __future__ import annotations
import random
from typing import List
from card import Card


class Deck:
    RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    SUITS = ["S", "H", "D", "C"]

    def __init__(self, num_decks: int = 1):
        """
        Build a standard 52-card deck (x num_decks) and shuffle.
        Must store remaining cards in self.cards.
        """
        self.cards: List[Card] = []
        # TODO (Member A): build deck into self.cards
        # TODO (Member A): shuffle deck
        raise NotImplementedError

    def shuffle(self) -> None:
        """Shuffle remaining cards."""
        # TODO (Member A): implement
        raise NotImplementedError

    def draw(self) -> Card:
        """
        Remove and return ONE card from the deck.
        Must not return duplicates.
        """
        # TODO (Member A): implement
        raise NotImplementedError

    def remaining(self) -> int:
        """Return number of remaining cards."""
        # TODO (Member A): implement
        raise NotImplementedError
