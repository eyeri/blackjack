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
       # TODO (Member A): Return exactly f"{rank}{suit}" (e.g., "AS", "10H"). No spaces.
    pass
    

    def base_value(self) -> int:
        """
        Return base blackjack value:
        - A -> 11
        - J/Q/K -> 10
        - number -> int(rank)
        """
        # TODO (Member A): Implement base blackjack values: A->11, J/Q/K->10, else int(rank).
        
        # TODO (Member A): Must NOT handle Ace-as-1 here; that logic belongs in Hand.best_total().
    pass
