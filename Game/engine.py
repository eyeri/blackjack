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
        self.second_hand = Hand()
        self.phase: Phase = Phase.INIT
        self.message: str = ""
        self.outcome_text: str = ""  # "WIN" | "LOSE" | "PUSH"

    def new_round(self) -> None:
        """
        Reset everything and deal initial cards.
        phase -> PLAYER_TURN
        """
        # Re-instantiate to ensure a fresh state and prevent data leakage from previous rounds.
        self.player.cards = []
        self.dealer.cards = []
        self.second_hand.cards = []
        self.deck.shuffle()
        self.initial_deal()
        self.outcome_text = ""
        if self.player.is_blackjack() or self.dealer.is_blackjack():
            self.resolve_round()
        else:
            self.phase = Phase.PLAYER_TURN
            self.message = "Player turn: HIT or STAND."
            
        
        

    def initial_deal(self) -> None:
        """Deal 2 cards to player and 2 cards to dealer."""
        self.player.add(self.deck.draw())
        self.player.add(self.deck.draw())
        self.dealer.add(self.deck.draw())
        self.dealer.add(self.deck.draw())
        # [Fixed] since there is if-else in new_round, this is enough
        

    def can_hit(self) -> bool:
        return self.phase == Phase.PLAYER_TURN and not self.player.is_bust()

    def can_stand(self) -> bool:
        """Return True if STAND is allowed now."""
        return self.phase == Phase.PLAYER_TURN and not self.player.is_bust()
        # [Fixed] since there is if-else in new_round, this is enough

    def player_hit(self) -> None:

        """Player draws one card. If bust -> ROUND_OVER."""
        if not self.can_hit():
            self.message = "Invalid action: HIT not allowed now." #text added
            return
        self.player.add(self.deck.draw())
        if self.player.is_bust():
            self.outcome_text = "LOSE" # text added
            self.phase = Phase.ROUND_OVER
            
            # [Fixed] Added dynamic messages to provide immediate feedback on the player's total and next available actions.
            self.message = f"Player busts with {self.player.base_total()}. LOSE."
        else:
            self.message = f"Player hits ({self.player.base_total()}). HIT or STAND?"


    def player_stand(self) -> None:
        """Switch to DEALER_TURN, run dealer, resolve, ROUND_OVER."""
        if not self.can_stand():
            self.message = "Invalid action: STAND not allowed now." # text added
            return
        self.phase = Phase.DEALER_TURN
        self.message = "Dealer turn" # text added
        self.run_dealer_turn()
        self.resolve_round()
        # [Fixed] since there is if-else in new_round, this is enough
        

    def run_dealer_turn(self) -> None:
        """Dealer hits while dealer.best_total() < 17."""
        while self.dealer.base_total() < 17:
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
        # [Fixed] Defined here to prevent UnboundLocalError if player busts
        player_total = self.player.base_total()
        dealer_total = self.dealer.base_total()

        if self.player.is_bust():
            self.outcome_text = "LOSE"


        elif self.dealer.is_bust():
            self.outcome_text = "WIN"
        else:
            if player_total > dealer_total:
                self.outcome_text = "WIN"
                
            elif dealer_total > player_total:
                self.outcome_text = "LOSE"
            else:
                # [Fixed] Added () to correctly execute the method call
                if self.player.is_blackjack() and not self.dealer.is_blackjack():
                    self.outcome_text = "WIN"
                elif not self.player.is_blackjack() and self.dealer.is_blackjack():
                    self.outcome_text = "LOSE"
                else:
                    self.outcome_text = "PUSH"
        self.message = f"Player {player_total} vs Dealer {dealer_total} {self.outcome_text}"
        self.phase = Phase.ROUND_OVER # [Fixed] Ensure the game state transitions to finished

    def state_snapshot(self, hide_dealer_hole: bool = True) -> dict:
    # Hiding dealer's first card during player turn to maintain game integrity.


    # Fallback logic for deck count to prevent AttributeError.
    

    # Returning string codes instead of objects for easier debugging.
        if hide_dealer_hole == True and self.phase == Phase.PLAYER_TURN:
            dealer_cards = ["hidden"] + [c.code() for c in self.dealer.cards[1:]]
            dealer_total = "hidden"
        else:
            dealer_cards = self.dealer.codes()
            dealer_total = self.dealer.base_total()

        if hasattr(self.deck, "cards"):
            deck_remaining = len(self.deck.cards)
        else:
            deck_remaining = 0

        if hasattr(self, "second_hand"):
            second_hand_cards = self.second_hand.codes()
            second_hand_total = self.second_hand.base_total()
        else:
            second_hand_cards = []
            second_hand_total = 0
        

        return {
            "phase": self.phase.name,
            "outcome_text": self.outcome_text,
            "player_cards": self.player.codes(),
            "second_hand_cards": second_hand_cards,
            "dealer_cards": dealer_cards,
            "player_total": self.player.base_total(),
            "second_hand_total": second_hand_total,
            "dealer_total": dealer_total,
            "deck_remaining": deck_remaining
            

        }
        

#Advanced Rule Extension

    def can_double_down(self) -> bool:
        """
        Return True if DOUBLE DOWN is allowed now.
        Typical conditions (for future):
        - first decision of the round
        - exactly 2 cards in player hand
        """
        return (
            self.phase == Phase.PLAYER_TURN 
            and len(self.player.cards) == 2
            and not self.player.is_bust()
        )

    def can_split(self) -> bool:
        """
        Return True if SPLIT is allowed now.
        Typical conditions (for future):
        - exactly 2 cards
        - both cards have same rank
        """
        return (
            self.phase == Phase.PLAYER_TURN
            and len(self.player.cards) == 2
            and self.player.cards[0].rank == self.player.cards[1].rank
            )

    def player_double_down(self) -> None:
        """
        Player doubles the bet, draws exactly one card,
        and then automatically stands.
        """
        if not self.can_double_down():
            self.message = "INVALID action: double down not allowed"
            return
            
            
        # bet doubles
        self.player_hit()
        if self.phase != Phase.ROUND_OVER:
            self.player_stand()

        self.message = "bet has doubled"


  
    def player_split(self) -> None:
        """
        Split the initial hand into two hands.
        """
        if not self.can_split():
            self.message = "INVALID action: SPLIT not allowed"
            return

        self.second_hand.cards = []

        card = self.player.cards.pop()
        self.second_hand.add(card)

        self.player.add(self.deck.draw())
        self.second_hand.add(self.deck.draw())
        self.message = "hand split into 2 hands"