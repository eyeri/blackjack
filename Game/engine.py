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
        self.second_hand = Hand()
        self.phase: Phase = Phase.INIT
        self.message: str = ""
        self.outcome_texts: dict[str, str] = {}  # e.g {"player": "WIN", "second_hand": "LOSE"}
        self.current_bet = 0
        self.hand_bets: dict[str, int] = {"player": 0, "second_hand": 0}
        self.player_balance = 1000

    def new_round(self) -> None:
        """
        Reset everything and deal initial cards.
        phase -> PLAYER_TURN
        """
        i = 0
        while i == 0:
            self.current_bet = int(input("Enter your bet: "))
            if self.current_bet > self.player_balance:
                self.current_bet = 0
                self.message = "INVALID BET not enough dollars"
            else:
                i = 1
                self.player_balance = self.player_balance - self.current_bet
        self.hand_bets["player"] = self.current_bet
        self.hand_bets["second_hand"] = 0
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
        Decide WIN/LOSE/PUSH, set message, phase=ROUND_OVER.
        Rules:
        - player bust -> lose
        - dealer bust -> win
        - compare totals -> win/lose/push
        - optional: blackjack checks
        """
        player_total = player_hand.base_total()
        dealer_total = dealer_hand.base_total()
        if player_hand.is_blackjack() and dealer_hand.is_blackjack():
            return "PUSH"
        elif player_hand.is_blackjack():
            return "WIN"
        elif dealer_hand.is_blackjack():
            return "LOSE"
        
        elif player_hand.is_bust():
            return "LOSE"
        elif dealer_hand.is_bust():
            return "WIN"

        else:
            if player_total > dealer_total:
                return "WIN"
            elif dealer_total > player_total:
                return "LOSE"
            else:
                return "PUSH"
        

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
        if not self.can_hit():
            self.message = "Invalid action: HIT not allowed now."
            return
        self.player.add(self.deck.draw())
        if self.player.is_bust():
            self.outcome_texts["player"] = "LOSE"
            self.phase = Phase.ROUND_OVER
            self.message = f"Player busts with {self.player.base_total()}. LOSE."
        else:
            self.message = f"Player hits ({self.player.base_total()}). HIT or STAND?"


    def player_stand(self) -> None:
        """Switch to DEALER_TURN, run dealer, resolve, ROUND_OVER."""
        if not self.can_stand():
            self.message = "Invalid action: STAND not allowed now."
            return
        self.phase = Phase.DEALER_TURN
        self.message = "Dealer turn"
        self.run_dealer_turn()
        self.resolve_round()
        

    def run_dealer_turn(self) -> None:
        """Dealer hits while dealer.base_total() < 17."""
        while self.dealer.base_total() < 17:
            self.dealer.add(self.deck.draw())
        

    def resolve_round(self) -> None:
        """
        Resolve the round for all hands (player and second hand if split),
        update outcome_texts, and adjust player_balance based on bets.
        """
        hands = [self.player]
        if self.second_hand.cards:
            hands.append(self.second_hand)
        
        self.outcome_texts = {}
        self.hand_bets = getattr(self,"hand_bets", {"player": self.current_bet, "second_hand": 0})

        dealer_total = self.dealer.base_total()

        for i, hand in enumerate(hands):
            key = "player" if i == 0 else "second_hand"

            result = self._evaluate_hand(hand, self.dealer)
            self.outcome_texts[key] = result
            
            bet = self.hand_bets.get(key, self.current_bet)

            if result == "WIN":
                if hand.is_blackjack():
                    # Blackjack pays 3:2
                    self.player_balance += int(bet * 2.5)
                else:
                    self.player_balance += bet * 2
            elif result == "PUSH":
                # Return bet
                self.player_balance += bet
        
        results_str = ", ".join(f"{k}: {v}" for k, v in self.outcome_texts.items())
        self.message = f"Dealer {dealer_total}. Results: {results_str}"
        self.phase = Phase.ROUND_OVER
        

    def state_snapshot(self, hide_dealer_hole: bool = True) -> dict:
        dealer_codes = self.dealer.codes()
        dealer_total: Optional[int] = self.dealer.base_total()
        if hide_dealer_hole and self.phase == Phase.PLAYER_TURN:
            dealer_cards = ["??"] + dealer_codes[1:]
            dealer_total = None
        else:
            dealer_cards = dealer_codes

        if hasattr(self.deck, "remaining"):
            deck_remaining = self.deck.remaining()
        elif hasattr(self.deck, "cards"):
            deck_remaining = len(self.deck.cards)
        else:
            deck_remaining = 0

        if hasattr(self, "second_hand"):
            second_hand_cards = self.second_hand.codes()
            second_hand_total = self.second_hand.base_total()
        else:
            second_hand_cards = []
            second_hand_total = None
        

        return {
            "phase": self.phase.name,
            "outcome_texts": self.outcome_texts,
            "player_cards": self.player.codes(),
            "second_hand_cards": second_hand_cards,
            "dealer_cards": dealer_cards,
            "player_total": self.player.base_total(),
            "second_hand_total": second_hand_total,
            "dealer_total": dealer_total,
            "deck_remaining": deck_remaining,
            "player_balance": self.player_balance,
            "current_bet": self.current_bet
        }
        

    # Advanced Rule Extension

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
        if not self.can_double_down():
            self.message = "INVALID action: double down not allowed"
            return
        self.player_balance -= self.current_bet
        self.current_bet *= 2
        
        self.player_hit()
        if self.phase != Phase.ROUND_OVER:
            self.player_stand()

        self.message = "Bet has doubled"

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