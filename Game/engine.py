from __future__ import annotations
from cmath import phase
from enum import Enum, auto
from typing import Dict, Any, Optional

from .deck import Deck
from .hand import Hand
from .card import Card


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
        self.second_hand: Hand = Hand()
        self.phase: Phase = Phase.INIT
        self.message: str = ""
        
        self.outcome_texts: dict[str, str] = {}  
        self.hand_bets: dict[str, int] = {"player": 0, "second_hand": 0}
        
        self.player_balance = 1000
        self.current_bet = 0
    @property
    def outcome_text(self) -> str:
        return self.outcome_texts.get("player", "")
    
    def player_surrender(self) -> None:
    # only able at first turn
        if self.phase == Phase.PLAYER_TURN and len(self.player.cards) == 2:
            refund = self.current_bet // 2
            self.player_balance += refund
            self.outcome_texts["player"] = "SURRENDER"
            self.phase = Phase.ROUND_OVER
            self.message = f"Surrendered. ${refund} returned to your balance."
            
    def new_round(self, bet_amount: int = 100):
        if self.player_balance < bet_amount:
            self.message = "Insufficient balance for this bet!"
            return
        if bet_amount > self.player_balance:
            self.message = "INVALID BET not enough dollars."
            bet_amount = 10
        
        self.current_bet = bet_amount
        self.player_balance -= self.current_bet
        self.hand_bets = {"player": self.current_bet, "second_hand": 0}
        
        self.deck = Deck(num_decks=1)
        self.player = Hand()
        self.dealer = Hand()
        self.second_hand = Hand()
        
        self.message = ""
        self.outcome_texts = {}
        self.phase = Phase.INIT
        self.initial_deal()
        
        if self.player.is_blackjack() or self.dealer.is_blackjack():
            self.resolve_round()
        else:
            self.phase = Phase.PLAYER_TURN
            self.message = "Player turn: HIT or STAND."
            
    def _evaluate_hand(self, player_hand: Hand, dealer_hand: Hand) -> str:
        """
        [TODO] Helper function to compare ONE hand against the dealer.
        This is crucial for Splitting later.
        
        Logic to implement:
        - If player busts -> "LOSE"
        - If dealer busts -> "WIN"
        - Compare totals: Higher wins, equal is "PUSH"
        - (Optional) Handle Blackjack priority
        """
        if player_hand.is_bust(): return "LOSE"
        if dealer_hand.is_bust(): return "WIN"
        
        p_total = player_hand.best_total()
        d_total = dealer_hand.best_total()
        
        if player_hand.is_blackjack() and not dealer_hand.is_blackjack(): return "WIN"
        if not player_hand.is_blackjack() and dealer_hand.is_blackjack(): return "LOSE"
        
        if p_total > d_total: return "WIN"
        elif d_total > p_total: return "LOSE"
        else: return "PUSH"
        

    def initial_deal(self) -> None:
        """Deal 2 cards to player and 2 cards to dealer."""
        self.player.add(self.deck.draw())
        self.dealer.add(self.deck.draw())
        self.player.add(self.deck.draw())
        self.dealer.add(self.deck.draw())
        

    def can_hit(self) -> bool:
        return self.phase == Phase.PLAYER_TURN and not self.player.is_bust()
    
    def can_stand(self) -> bool:
        """Return True if STAND is allowed now."""
        return self.phase == Phase.PLAYER_TURN and not self.player.is_bust()
    
    def player_hit(self) -> None:

        """Player draws one card. If bust -> ROUND_OVER."""
        if self.phase != Phase.PLAYER_TURN: return
        
        self.player.add(self.deck.draw())
        if self.player.is_bust():
            self.outcome_texts["player"] = "LOSE"
            self.resolve_round()
        else:
            self.message = f"Player hits ({self.player.best_total()}). HIT or STAND?"


    def player_stand(self) -> None:
        if self.phase != Phase.PLAYER_TURN: return
        self.phase = Phase.DEALER_TURN
        self.run_dealer_turn()
        self.resolve_round()
        

    def run_dealer_turn(self) -> None:
        """Dealer hits while dealer.base_total() < 17."""
        while self.dealer.best_total() < 17:
            self.dealer.add(self.deck.draw())
        

    def resolve_round(self) -> None:
        hands = {"player": self.player}
        if self.second_hand.cards: 
            hands["second_hand"] = self.second_hand
            
        for key, hand in hands.items():
            result = self._evaluate_hand(hand, self.dealer)
            self.outcome_texts[key] = result
            
            bet = self.hand_bets.get(key, 0)
            if result == "WIN":
                multiplier = 2.5 if hand.is_blackjack() else 2.0
                self.player_balance += int(bet * multiplier)
            elif result == "PUSH":
                self.player_balance += bet
        
        self.message = f"dealer {self.dealer.best_total()}. Result: " + \
                       ", ".join([f"{k}:{v}" for k, v in self.outcome_texts.items()])
        self.phase = Phase.ROUND_OVER

    def state_snapshot(self, hide_dealer_hole: bool = True) -> dict:
        # [Fix #3] Hole card hiding should keep types consistent:
        # - hide first dealer card as "??"
        # - dealer_total should be None while hidden (not a string)
        dealer_codes = self.dealer.codes()
        if hide_dealer_hole and self.phase == Phase.PLAYER_TURN:
            dealer_display = ["??"] + dealer_codes[1:]
            dealer_total = None
        else:
            dealer_display = dealer_codes
            dealer_total = self.dealer.best_total()

        return {
            "phase": self.phase.name,
            "outcome_text": self.outcome_text, 
            "outcome_texts": self.outcome_texts,
            "player_cards": self.player.codes(),
            "second_hand_cards": self.second_hand.codes() if self.second_hand.cards else [],
            "dealer_cards": dealer_display,
            "player_total": self.player.best_total(),
            "dealer_total": dealer_total,
            "player_balance": self.player_balance,
            "current_bet": self.current_bet
        }
    

    #Advanced Rule Extension

    def can_double_down(self) -> bool:
        return (
            self.phase == Phase.PLAYER_TURN 
            and len(self.player.cards) == 2
            and not self.player.is_bust()
            and self.player_balance >= self.current_bet
        )
    
    def can_split(self) -> bool:
        return (
            self.phase == Phase.PLAYER_TURN
            and len(self.player.cards) == 2
            and self.player.cards[0].rank == self.player.cards[1].rank
            and self.player_balance >= self.current_bet
        )

    def player_double_down(self) -> None:
        """
        Player doubles the bet, draws exactly one card,
        and then automatically stands.
        """

        """
        [TODO] Double the bet, draw one card, and stand.
        
        Logic to implement:
        1. Check if doubling is allowed (can_double_down)
        2. Check if player has enough balance for the additional bet
        3. Deduct additional bet from balance, double current_bet
        4. Draw EXACTLY one card
        5. Trigger resolution (resolve_round or player_stand)
        """
        if not self.can_double_down(): return

        if not self.can_double_down(): 
            self.message = "Double down is not allowed."
            return
        
        self.player_balance -= self.current_bet
        self.current_bet *= 2
        self.hand_bets["player"] = self.current_bet 
        
        self.player.add(self.deck.draw())
        
        if self.player.is_bust():
            self.outcome_texts["player"] = "LOSE"
            self.resolve_round()
        else:
            self.player_stand()

    def player_split(self) -> None:
        if not self.can_split():
            self.message = "INVALID action: SPLIT not allowed"
            return

        self.second_hand.cards = []

        card = self.player.cards.pop()
        self.second_hand.add(card)

        self.player.add(self.deck.draw())
        self.second_hand.add(self.deck.draw())

        self.hand_bets["second_hand"] = self.hand_bets["player"]
        self.message = "Hand split into 2 hands"
