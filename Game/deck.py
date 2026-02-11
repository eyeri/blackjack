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
        # TODO (Member A): Build deck into self.cards in a consistent order (deterministic before shuffle).

        # TODO (Member A): Call shuffle() exactly once here (avoid hidden reshuffles elsewhere).

        # TODO (Member A): Store remaining cards ONLY in self.cards (no duplicates).

        # TODO (Member A): If num_decks < 1, raise ValueError.
    pass

    def shuffle(self) -> None:
        """Shuffle remaining cards."""
        # TODO (Member A): Use random.shuffle(self.cards). Do not recreate cards here.

        # TODO (Member A): No extra randomness outside shuffle()/__init__ (supports reproducible session restore).
    pass

    def draw(self) -> Card:
        """
        Remove and return ONE card from the deck.
        Must not return duplicates.
        """
        # TODO (Member A): Remove ONE card from a consistent end (recommend: self.cards.pop()).

        # TODO (Member A): Must never return duplicates; draw must reduce remaining().

        # TODO (Member A): Decide behavior when empty (raise RuntimeError recommended).
    pass

    def remaining(self) -> int:
        """Return number of remaining cards."""
        # TODO (Member A): Return len(self.cards).
    pass 