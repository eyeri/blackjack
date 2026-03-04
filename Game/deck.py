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
        if num_decks < 1:
            raise ValueError("num_decks must be at least 1")

        self.cards: List[Card] = []

        # Build deck in deterministic order before shuffle
        for _ in range(num_decks):
            for suit in self.SUITS:
                for rank in self.RANKS:
                    self.cards.append(Card(rank=rank, suit=suit)) # [Fixed] Using keyword arguments for better readability when instantiating Card.

        # Shuffle exactly once
        self.shuffle()

    def shuffle(self) -> None:
        """Shuffle remaining cards."""
        random.shuffle(self.cards)

    def draw(self) -> Card:
        """
        Remove and return ONE card from the deck.
        Must not return duplicates.
        """
        if not self.cards:
            raise RuntimeError("Cannot draw from empty deck")

        return self.cards.pop()

    def remaining(self) -> int:
        """Return number of remaining cards."""
        return len(self.cards)