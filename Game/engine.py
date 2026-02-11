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
        # TODO (Member C): Reset deck/player/dealer + clear message/outcome; then initial_deal().

        # TODO (Member C): phase must end as PLAYER_TURN (unless immediate resolve like blackjack).
    pass

    def initial_deal(self) -> None:
        """Deal 2 cards to player and 2 cards to dealer."""
        # TODO (Member C): Deal 2 cards each (player, dealer, player, dealer) using deck.draw().
    pass 

    def can_hit(self) -> bool:
        """Return True if HIT is allowed now."""
        # TODO (Member C): Return True only during PLAYER_TURN and round not over.
    pass

    def can_stand(self) -> bool:
        """Return True if STAND is allowed now."""
        # TODO (Member C): Return True only during PLAYER_TURN and round not over.
    pass 

    def player_hit(self) -> None:
        """Player draws one card. If bust -> ROUND_OVER."""
        # TODO (Member C): If can_hit, draw one card; if player busts -> outcome=LOSE and phase=ROUND_OVER.
    pass 

    def player_stand(self) -> None:
        """Switch to DEALER_TURN, run dealer, resolve, ROUND_OVER."""
        # TODO (Member C): Switch to DEALER_TURN, run_dealer_turn(), then resolve_round() and set ROUND_OVER.
    pass 

    def run_dealer_turn(self) -> None:
        """Dealer hits while dealer.best_total() < 17."""
        # TODO (Member C): Dealer hits while dealer.best_total() < 17 (S17 rule).
    pass

    def resolve_round(self) -> None:
        """
        Decide WIN/LOSE/PUSH, set message, phase=ROUND_OVER.
        Rules:
        - player bust -> lose
        - dealer bust -> win
        - compare totals -> win/lose/push
        - optional: blackjack checks
        """
        # TODO (Member C): (Milestone 2) You may ignore blackjack priority if not required; document limitation in milestone report.
    pass

    def state_snapshot(self, hide_dealer_hole: bool = True) -> Dict[str, Any]:
        """
        Return dict for printing/debugging (no UI code):
        - phase, message, outcome_text
        - player_cards, dealer_cards (optionally hide dealer first card)
        - player_total, dealer_total (optional hidden)
        - deck_remaining
        """
        # TODO (Member C): Return a dict with stable keys: phase, message, outcome_text, player_cards, dealer_cards, totals, deck_remaining.

        # TODO (Member C): If hide_dealer_hole and phase==PLAYER_TURN, replace dealer first card with "??" and hide dealer_total (None).
    pass

#Advanced Rule Extension
# TODO (Milestone 3+ only): Advanced actions (DOUBLE / SPLIT). Do NOT implement for Milestone 2 submission.
# TODO (Member C): Implement only after core loop (NEW/HIT/STAND/RESOLVE) is stable and tested.

    def can_double_down(self) -> bool:
        """
        Return True if DOUBLE DOWN is allowed now.
        Typical conditions (for future):
        - first decision of the round
        - exactly 2 cards in player hand
        """
        # TODO (Member C): implement 
    pass

    def can_split(self) -> bool:
        """
        Return True if SPLIT is allowed now.
        Typical conditions (for future):
        - exactly 2 cards
        - both cards have same rank
        """
        # TODO (Member C): implement 
    pass

    def player_double_down(self) -> None:
        """
        Player doubles the bet, draws exactly one card,
        and then automatically stands.
        """
        # TODO (Member C): implement 
    pass 

    def player_split(self) -> None:
        """
        Split the initial hand into two hands.
        """
        # TODO (Member C): implement 
    pass 
