from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Card:
    """
    rank: "A","2"...,"10","J","Q","K"
    suit: "S","H","D","C"
    """
    rank: str
    suit: str

    def code(self) -> str:
        """Return ASCII code like 'AS', '10H', 'KD'."""
        return f"{self.rank}{self.suit}"

    def base_value(self) -> int:
        """
        Return base blackjack value:
        - A -> 11
        - J/Q/K -> 10
        - number -> int(rank)
        """
        if self.rank == "A":
            return 11
        if self.rank in ["J", "Q", "K"]:
            return 10
        return int(self.rank)