"""
===============================================================================
ENGINE.PY - MILESTONE 4 WORK GUIDE
===============================================================================

This file is being upgraded from a single-player engine to a multiplayer engine.

Old structure:
- one player
- optional second hand
- one global bet / balance flow

New structure:
- multiple players
- each player can have multiple hands
- each hand has its own bet and result
- turn flow must track:
    current_player_index
    current_hand_index

Main idea:
Do not mix old single-player fields with new multiplayer fields.

Wrong direction:
- using self.player in one function
- using self.players in another function

Correct direction:
- use the new multiplayer state model everywhere

----------------------------------------------------------------------------
What is already changed
----------------------------------------------------------------------------
These parts are already moved to the new structure:
- __init__
- start_betting_round()
- complete_betting_and_deal()
- _current_hand()
- _current_bet()
- _turn_message()
- _set_current_outcome()
- _all_hands_finished_or_blocked()
- _advance_turn()
- _evaluate_hand
- state_snapshot()
- _initial_deal_all()
- resolve_round()
- player_hit()
- player_stand()
- player_double_down()
- player_surrender()
- player_split()

----------------------------------------------------------------------------
What still must be rewritten
----------------------------------------------------------------------------
1. Action guards
- can_hit()
- can_stand()
- can_double_down()
- can_split()
- can_surrender()

----------------------------------------------------------------------------
What should no longer be the main flow
----------------------------------------------------------------------------
These old single-player functions should not drive Milestone 4 anymore:
- new_round()
- initial_deal()

New main flow:
START/NEW
-> start_betting_round()
-> complete_betting_and_deal()
-> player turns
-> dealer turn
-> resolve_round()

----------------------------------------------------------------------------
Rule for anyone editing this file
----------------------------------------------------------------------------
Before writing or changing any function, check this first:

1. Am I using current player / current hand?
2. Am I reading from players / player_bets / player_balances?
3. Am I avoiding old fields like self.player, self.current_bet, self.second_hand?

If the answer is no, the function is still using the old engine model.

===============================================================================
"""
from __future__ import annotations
from cmath import phase
from enum import Enum, auto
from typing import List
from typing import Dict, Any, Optional

from .deck import Deck
from .hand import Hand
from .card import Card


class Phase(Enum):
    INIT = auto()
    BETTING = auto() # new for milestone 4
    PLAYER_TURN = auto()
    DEALER_TURN = auto()
    ROUND_OVER = auto()


class GameEngine:

    """[Fixed]"""
    def __init__(self, num_players: int = 1, is_tutorial: bool = False):
        self.num_players = max(1, int(num_players))
        self.is_tutorial = bool(is_tutorial)

        self.deck: Deck = Deck(num_decks=6)
        self.dealer: Hand = Hand()
        self.phase: Phase = Phase.INIT
        self.message: str = ""

        # Each player owns a list of hands.
        # Normally 1 hand. After split -> 2 hands.
        self.players: List[List[Hand]] = [[Hand()] for _ in range(self.num_players)]
        self.player_bets: List[List[int]] = [[0] for _ in range(self.num_players)]
        self.player_balances: List[int] = [1000 for _ in range(self.num_players)]
        self.outcome_texts: List[List[str]] = [[""] for _ in range(self.num_players)]

        self.current_player_index: int = 0
        self.current_hand_index: int = 0

        self.tutorial_message: str = (
            "Welcome to Tutorial Mode. Place your bet to begin."
            if self.is_tutorial else ""
        )
    
    # ----------------------------
    # round setup (milestone 4)
    # ----------------------------

    """[Changed to "start_betting_roung + complete_betting_and_deal"]       
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
    """

    """[Added]"""
    def start_betting_round(self) -> None:
        self.deck = Deck(num_decks=6)
        self.dealer = Hand()
        self.players = [[Hand()] for _ in range(self.num_players)]
        self.player_bets = [[0] for _ in range(self.num_players)]
        self.outcome_texts = [[""] for _ in range(self.num_players)]
        self.current_player_index = 0
        self.current_hand_index = 0
        self.phase = Phase.BETTING
        self.message = "Place bets for all players, then press DEAL."

        if self.is_tutorial:
            self.tutorial_message = (
                "Tutorial mode: place your bet first. "
                "After the deal, the system will recommend the strongest action."
            )

    """[Added]"""
    def complete_betting_and_deal(self, bets: List[int]) -> None:
        if self.phase != Phase.BETTING:
            return

        if len(bets) != self.num_players:
            self.message = "Invalid betting data."
            return

        normalized_bets: List[int] = []
        for i, raw_bet in enumerate(bets):
            try:
                bet = int(raw_bet)
            except Exception:
                bet = 10

            if bet <= 0:
                bet = 10

            if bet > self.player_balances[i]:
                self.message = f"Player {i + 1} does not have enough balance."
                return

            normalized_bets.append(bet)

        for i, bet in enumerate(normalized_bets):
            self.player_balances[i] -= bet
            self.player_bets[i][0] = bet

        self._initial_deal_all()

        self.current_player_index = 0
        self.current_hand_index = 0

        if self._all_hands_finished_or_blocked():
            self.phase = Phase.DEALER_TURN
            self.run_dealer_turn()
            self.resolve_round()
        else:
            self.phase = Phase.PLAYER_TURN
            self.message = self._turn_message()
        
    """[Changed to _initial_deal_all]
    def initial_deal(self) -> None:
        Deal 2 cards to player and 2 cards to dealer.

        self.player.add(self.deck.draw())
        self.dealer.add(self.deck.draw())
        self.player.add(self.deck.draw())
        self.dealer.add(self.deck.draw())
    """

    def _initial_deal_all(self) -> None:
        # action guards (TODO - must be rewritten before player actions work correctly)
        raise NotImplementedError
    
    # ----------------------------
    # helpers
    # ----------------------------

    """[Added]"""
    def _current_hand(self) -> Hand:
        return self.players[self.current_player_index][self.current_hand_index]

    """[Added]"""
    def _current_bet(self) -> int:
        return self.player_bets[self.current_player_index][self.current_hand_index]

    """[Added]"""
    def _turn_message(self) -> str:
        return (
            f"Player {self.current_player_index + 1} / "
            f"Hand {self.current_hand_index + 1}: choose an action."
        )

    """[Fixed]"""
    def _set_current_outcome(self, text: str) -> None:
        self.outcome_texts[self.current_player_index][self.current_hand_index] = text

    """[Added]"""
    def _all_hands_finished_or_blocked(self) -> bool:
        for p in range(self.num_players):
            for h in range(len(self.players[p])):
                hand = self.players[p][h]
                if not hand.is_blackjack() and not hand.is_bust():
                    return False
        return True
    
    """[Added]"""
    def _advance_turn(self) -> None:
        while True:
            if self.current_player_index >= self.num_players:
                self.phase = Phase.DEALER_TURN
                self.run_dealer_turn()
                self.resolve_round()
                return

            hands = self.players[self.current_player_index]

            while self.current_hand_index < len(hands):
                hand = hands[self.current_hand_index]
                outcome = self.outcome_texts[self.current_player_index][self.current_hand_index]

                if outcome:
                    self.current_hand_index += 1
                    continue

                if hand.is_blackjack():
                    self.outcome_texts[self.current_player_index][self.current_hand_index] = "BLACKJACK"
                    self.current_hand_index += 1
                    continue

                if hand.is_bust():
                    self.outcome_texts[self.current_player_index][self.current_hand_index] = "LOSE"
                    self.current_hand_index += 1
                    continue

                self.message = self._turn_message()
                return

            self.current_player_index += 1
            self.current_hand_index = 0
    
    """[Fixed]"""    
    def _evaluate_hand(self, player_hand: Hand, dealer_hand: Hand) -> str:
        """
        Compare one player hand against the dealer hand.
        This helper is reusable for split hands and multiplayer resolution.
        """
        if player_hand.is_bust():
            return "LOSE"
        if dealer_hand.is_bust():
            return "WIN"

        p_total = player_hand.best_total()
        d_total = dealer_hand.best_total()

        if player_hand.is_blackjack() and not dealer_hand.is_blackjack():
            return "BLACKJACK"
        if not player_hand.is_blackjack() and dealer_hand.is_blackjack():
            return "LOSE"

        if p_total > d_total:
            return "WIN"
        elif d_total > p_total:
            return "LOSE"
        else:
            return "PUSH"
        
    # ----------------------------
    # action guards
    # TODO (must rewrite):
    # This function still uses the old single player model.
    # Do not patch self.player / self.current_bet.
    # Rewrite using _current_hand(), _current_bet(), player_bets, player_balances.
    # ----------------------------   

    def can_hit(self) -> bool:
        return self.phase == Phase.PLAYER_TURN and not self._current_hand().is_bust()
    
    def can_stand(self) -> bool:
        """Return True if STAND is allowed now."""
        return self.phase == Phase.PLAYER_TURN and not self._current_hand().is_bust()
    
    def can_double_down(self) -> bool:
        return (
            self.phase == Phase.PLAYER_TURN 
            and len(self._current_hand().cards) == 2
            and not self._current_hand().is_bust()
            and self.player_balances[self.current_player_index] >= self._current_bet()
        )
    
    def can_split(self) -> bool:
        return (
            self.phase == Phase.PLAYER_TURN
            and len(self._current_hand().cards) == 2
            and self._current_hand().cards[0].rank == self._current_hand().cards[1].rank
            and self.player_balances[self.current_player_index] >= self._current_bet()
        )
    
    def can_surrender(self) -> bool:
        #TODO
        raise NotImplementedError

    # ----------------------------
    # player actions
    # ----------------------------

    def player_hit(self) -> None:

        """Player draws one card. If bust -> ROUND_OVER."""
        if not self.can_hit(): 
            self.message = "HIT is not allowed right now"
            return

        hand = self._current_hand()
        hand.add(self.deck.draw())
        if hand.is_bust():
            self._set_current_outcome("LOSE")
            self.current_hand_index += 1
            self._advance_turn()
        else:
            self.message = f"Player {self.current_player_index + 1} hits ({hand.best_total()}). HIT or STAND?"


    def player_stand(self) -> None:
        if not self.can_stand(): 
            self.message = "STAND is not allowed right now"
            return

        self._set_current_outcome("STAND")
        self.current_hand_index += 1
        self._advance_turn()

    def player_double_down(self) -> None:
        if not self.can_double_down(): 
            self.message = "Double down is not allowed."
            return
        
        
        p = self.current_player_index
        h = self.current_hand_index
        bet = self.player_bets[p][h]

        self.player_balances[p] -= bet
        self.player_bets[p][h] += bet

        hand = self.players[p][h]
        hand.add(self.deck.draw())

        if hand.is_bust():
            self.outcome_texts[p][h] = "LOSE"
        else:
            self.outcome_texts[p][h] = "STAND"
        
        self.current_hand_index += 1
        self._advance_turn()

    def player_surrender(self) -> None:
    # only able at first turn
        if not self.can_surrender():
            self.message = "SURRENDER IS NOT ALLOWED"
            return
        
        p = self.current_player_index
        h = self.current_hand_index

        bet = self.player_bets[p][h]

        refund = bet // 2
        self.player_balances[p] += refund

        self._set_current_outcome("SURRENDER")

        self.current_hand_index += 1
        self._advance_turn()


    def player_split(self) -> None:
        if not self.can_split():
            self.message = "INVALID action: SPLIT not allowed"
            return

        p = self.current_player_index
        h = self.current_hand_index

        hand = self._current_hand()
        bet = self.player_bets[p][h]

        new_hand = Hand()

        card = hand.cards.pop()
        new_hand.add(card)

        hand.add(self.deck.draw())
        new_hand.add(self.deck.draw())

        self.players[p].insert(h + 1, new_hand)
        self.player_bets[p].insert(h + 1, bet)
        self.outcome_texts[p].insert(h + 1, "")

        self.player_balances[p] -= bet

        self.message = self._turn_message()

        
    # ----------------------------
    # dealer + resolve 
    # ----------------------------

    def run_dealer_turn(self) -> None:
        """Dealer hits while dealer.base_total() < 17."""
        while self.dealer.best_total() < 17:
            self.dealer.add(self.deck.draw())
        

    def resolve_round(self) -> None:
        summary_parts = [f"Dealer: {self.dealer.best_total()}"]

        for p in range(self.num_players):
            for h in range(len(self.players[p])):
                hand = self.players[p][h]
                existing = self.outcome_texts[p][h]

                if existing in ("SURRENDER", "LOSE"):
                    result = existing
                elif existing == "BLACKJACK":
                    result = "BLACKJACK"
                else:
                    result = self._evaluate_hand(hand, self.dealer)

                self.outcome_texts[p][h] = result
                bet = self.player_bets[p][h]

                if result == "BLACKJACK":
                    self.player_balances[p] += int(bet * 2.5)
                elif result == "WIN":
                    self.player_balances[p] += int(bet * 2.0)
                elif result == "PUSH":
                    self.player_balances[p] += bet

                summary_parts.append(f"P{p + 1}-H{h + 1}:{result}")

        self.phase = Phase.ROUND_OVER
        self.message = " | ".join(summary_parts)

    # ----------------------------
    # tutorial helper
    # ----------------------------

    """[Added]"""
    def get_advice(self) -> str:
        if not self.is_tutorial or self.phase != Phase.PLAYER_TURN:
            return ""

        hand = self._current_hand()

        if len(self.dealer.cards) < 2:
            return ""

        p_total = hand.best_total()
        dealer_up = self.dealer.cards[1].base_value()

        if self.can_split() and hand.cards[0].rank in ("A", "8"):
            return "Recommended: SPLIT"

        if self.can_double_down() and p_total in (10, 11) and dealer_up <= 9:
            return "Recommended: DOUBLE"

        if p_total <= 11:
            return "Recommended: HIT"
        if p_total >= 17:
            return "Recommended: STAND"
        if 12 <= p_total <= 16:
            return "Recommended: STAND" if dealer_up <= 6 else "Recommended: HIT"

        return "Recommended: HIT"

    """[Fixed]"""
    def state_snapshot(self, hide_dealer_hole: bool = True) -> dict:
        """
        Debug / inspection snapshot for the current Milestone 4 engine state.
        This is no longer a single-player UI snapshot.
        """

        dealer_codes = self.dealer.codes()
        if (
            hide_dealer_hole
            and self.phase == Phase.PLAYER_TURN
            and len(dealer_codes) >= 2
        ):
            dealer_display = ["??"] + dealer_codes[1:]
            dealer_total = None
        else:
            dealer_display = dealer_codes
            dealer_total = self.dealer.best_total() if self.dealer.cards else None

        return {
            "phase": self.phase.name,
            "message": self.message,
            "is_tutorial": self.is_tutorial,
            "tutorial_message": self.tutorial_message,
            "dealer_cards": dealer_display,
            "dealer_total": dealer_total,
            "current_player_index": self.current_player_index,
            "current_hand_index": self.current_hand_index,
            "players": [
                {
                    "player_index": p,
                    "balance": self.player_balances[p],
                    "hands": [
                        {
                            "hand_index": h,
                            "cards": hand.codes(),
                            "total": hand.best_total() if hand.cards else None,
                            "bet": self.player_bets[p][h],
                            "outcome": self.outcome_texts[p][h],
                            "is_turn": (
                                self.phase == Phase.PLAYER_TURN
                                and p == self.current_player_index
                                and h == self.current_hand_index
                            ),
                        }
                        for h, hand in enumerate(self.players[p])
                    ],
                }
                for p in range(self.num_players)
            ],
        }
    

    