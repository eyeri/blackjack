from __future__ import annotations
from cmath import phase
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
        self.player.cards = []
        self.dealer.cards = []
        self.deck.shuffle()
        self.outcome_text = ""
        self.initial_deal()
        if self.player.is_blackjack() == True or self.dealer.is_blackjack != True:
            self.resolve_round()
        else:
            self.phase = Phase.PLAYER_TURN
            self.message = "Player turn: HIT or STAND"
            
        
        

    def initial_deal(self) -> None:
        """Deal 2 cards to player and 2 cards to dealer."""
        self.player.add(self.deck.draw())
        self.player.add(self.deck.draw())
        self.dealer.add(self.deck.draw())
        self.dealer.add(self.deck.draw())
        self.phase = Phase.PLAYER_TURN
        

    def can_hit(self) -> bool:
        return self.phase == Phase.PLAYER_TURN and not self.player.is_bust()

    def can_stand(self) -> bool:
        """Return True if STAND is allowed now."""
        if self.phase == Phase.PLAYER_TURN and not self.player.is_bust():
            return True
        else:
            return False

    def player_hit(self) -> None:

        """Player draws one card. If bust -> ROUND_OVER."""
        if not self.can_hit():
            return
        self.player.add(self.deck.draw())
        if self.player.is_bust():
            self.phase = Phase.ROUND_OVER

    def player_stand(self) -> None:
        """Switch to DEALER_TURN, run dealer, resolve, ROUND_OVER."""
        if not self.can_stand():
            return
        self.phase = Phase.DEALER_TURN
        self.run_dealer_turn()
        self.resolve_round()
        self.phase = Phase.ROUND_OVER
        

    def run_dealer_turn(self) -> None:
        """Dealer hits while dealer.best_total() < 17."""
        while self.dealer.best_total() < 17:
            self.dealer.add(self.deck.draw())
        

    def resolve_round(self) -> None:
        """
        Decide WIN/LOSE/PUSH, set message, phase=ROUND_OVER.
        Rules:
        - player bust -> lose
        - dealer bust -> win
        - compare totals -> win/lose/push
        - optional: blackjack checks
        """
        if self.player.is_bust():
            self.outcome_text = "LOSE"


        elif self.dealer.is_bust():
            self.outcome_text = "WIN"
        else:
            player_total = self.player.best_total()
            dealer_total = self.dealer.best_total()
            if player_total > dealer_total:
                self.outcome_text = "WIN"
                
            elif dealer_total > player_total:
                self.outcome_text = "LOSE"
            else:
                if self.player.is_blackjack == True and self.dealer.is_blackjack != True:
                    self.outcome_text = "WIN"
                elif self.player.is_blackjack != True and self.dealer.is_blackjack == True:
                    self.outcome_text = "LOSE"
                else:
                    self.outcome_text = "PUSH"
        self.message = f"Player {player_total} vs Dealer {dealer_total} {self.outcome_text}"
        

    def state_snapshot(self, hide_dealer_hole: bool = True) -> Dict[str, Any]:
        """
        Return dict for printing/debugging (no UI code):
        - phase, message, outcome_text
        - player_cards, dealer_cards (optionally hide dealer first card)
        - player_total, dealer_total (optional hidden)
        - deck_remaining
        """
        return {
            "phase": self.phase.name,
            "outcome_text": self.outcome_text,
            "player_total": self.player.base_total(),
            "dealer_total": self.dealer.base_total(),
            "deck_remaining": len(self.deck.cards)

        }
        

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

