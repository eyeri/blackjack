from __future__ import annotations
from enum import Enum, auto
from typing import Dict, Any, Optional

from deck import Deck
from hand import Hand


class Phase(Enum):
    INIT = auto()
    PLAYER_TURN = auto()
    DEALER_TURN = auto()
    ROUND_OVER = auto()


class GameEngine:
    """
    Milestone 2 (no UI):
    - 1 player vs 1 dealer
    - Actions: HIT / STAND / NEW ROUND
    - Dealer rule: hit until total >= 17 (S17)
    """
    def __init__(self):
        self.deck: Deck = Deck(num_decks=1)
        self.player: Hand = Hand()
        self.dealer: Hand = Hand()
        self.phase: Phase = Phase.INIT
        self.message: str = ""
        self.outcome_text: str = ""  # "WIN" | "LOSE" | "PUSH"

    def new_round(self) -> None:
        """
        Reset everything and deal initial cards.
        phase -> PLAYER_TURN
        """
        # TODO (Member C): implement
        raise NotImplementedError

    def initial_deal(self) -> None:
        """Deal 2 cards to player and 2 cards to dealer."""
        # TODO (Member C): implement
        raise NotImplementedError

    def can_hit(self) -> bool:
        """Return True if HIT is allowed now."""
        # TODO (Member C): implement
        raise NotImplementedError

    def can_stand(self) -> bool:
        """Return True if STAND is allowed now."""
        # TODO (Member C): implement
        raise NotImplementedError

    def player_hit(self) -> None:
        """Player draws one card. If bust -> ROUND_OVER."""
        # TODO (Member C): implement
        raise NotImplementedError

    def player_stand(self) -> None:
        """Switch to DEALER_TURN, run dealer, resolve, ROUND_OVER."""
        # TODO (Member C): implement
        raise NotImplementedError

    def run_dealer_turn(self) -> None:
        """Dealer hits while dealer.best_total() < 17."""
        # TODO (Member C): implement
        raise NotImplementedError

    def resolve_round(self) -> None:
        """
        Decide WIN/LOSE/PUSH, set message, phase=ROUND_OVER.
        Rules:
        - player bust -> lose
        - dealer bust -> win
        - compare totals -> win/lose/push
        - optional: blackjack checks
        """
        # TODO (Member C): implement
        raise NotImplementedError

    def state_snapshot(self, hide_dealer_hole: bool = True) -> Dict[str, Any]:
        """
        Return dict for printing/debugging (no UI code):
        - phase, message, outcome_text
        - player_cards, dealer_cards (optionally hide dealer first card)
        - player_total, dealer_total (optional hidden)
        - deck_remaining
        """
        # TODO (Member C): implement
        raise NotImplementedError

#Advanced Rule Extension

    def can_double_down(self) -> bool:
        """
        Return True if DOUBLE DOWN is allowed now.
        Typical conditions (for future):
        - first decision of the round
        - exactly 2 cards in player hand
        """
        # TODO (Member C): implement 
        raise NotImplementedError

    def can_split(self) -> bool:
        """
        Return True if SPLIT is allowed now.
        Typical conditions (for future):
        - exactly 2 cards
        - both cards have same rank
        """
        # TODO (Member C): implement 
        raise NotImplementedError

    def player_double_down(self) -> None:
        """
        Player doubles the bet, draws exactly one card,
        and then automatically stands.
        """
        # TODO (Member C): implement 
        raise NotImplementedError

    def player_split(self) -> None:
        """
        Split the initial hand into two hands.
        """
        # TODO (Member C): implement 
        raise NotImplementedError

