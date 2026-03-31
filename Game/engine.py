from __future__ import annotations
from enum import Enum, auto
from typing import List

from .deck import Deck
from .hand import Hand


class Phase(Enum):
    INIT = auto()
    WAITING = auto()
    BETTING = auto()
    PLAYER_TURN = auto()
    DEALER_TURN = auto()
    ROUND_OVER = auto()


class GameEngine:
    BLACKJACK_PAYOUT = 1.5
    DEFAULT_BALANCE = 1000
    DEFAULT_MIN_BET = 10

    """[Fixed]"""
    def __init__(self, num_players: int = 2, is_tutorial: bool = False):
        self.num_players = max(1, int(num_players))
        self.is_tutorial = bool(is_tutorial)

        self.deck: Deck = Deck(num_decks=6)
        self.dealer: Hand = Hand()
        self.players: List[List[Hand]] = [[Hand()] for _ in range(self.num_players)]
        self.player_bets: List[List[int]] = [[0] for _ in range(self.num_players)]
        self.player_balances: List[int] = [self.DEFAULT_BALANCE for _ in range(self.num_players)]
        self.outcome_texts: List[List[str]] = [[""] for _ in range(self.num_players)]
        self.player_names: List[str] = [f"Player {i + 1}" for i in range(self.num_players)]
        self.player_ready: List[bool] = [False for _ in range(self.num_players)]
        self.bet_confirmed: List[bool] = [False for _ in range(self.num_players)]

        self.phase: Phase = Phase.WAITING
        self.message: str = "Waiting for players to join."
        self.tutorial_message: str = ""
        self.current_player_index: int = 0
        self.current_hand_index: int = 0
    
    # ----------------------------
    # round setup (milestone 4)
    # ----------------------------

    """[Added]"""
    def set_player_name(self, seat_index: int, name: str) -> None:
        if 0 <= seat_index < self.num_players:
            clean = (name or "").strip()
            self.player_names[seat_index] = clean[:32] if clean else f"Player {seat_index + 1}"
    
    """[Added]"""
    def set_player_ready(self, seat_index: int, ready: bool = True) -> None:
        if 0 <= seat_index < self.num_players:
            self.player_ready[seat_index] = bool(ready)
            if self.phase == Phase.WAITING:
                waiting_for = [
                    self.player_names[i]
                    for i, flag in enumerate(self.player_ready)
                    if not flag
                ]
                if waiting_for:
                    self.message = "Waiting for: " + ", ".join(waiting_for)
                else:
                    self.message = "All players joined. Host can start betting setup."

    """[Added]"""
    def all_players_ready(self) -> bool:
        return all(self.player_ready)


    """[Added]"""
    def start_betting_round(self) -> None:
        if not self.all_players_ready():
            self.message = "All seats must be occupied before a round can start."
            return

        self.deck = Deck(num_decks=6)
        self.dealer = Hand()
        self.players = [[Hand()] for _ in range(self.num_players)]
        self.player_bets = [[0] for _ in range(self.num_players)]
        self.outcome_texts = [[""] for _ in range(self.num_players)]
        self.current_player_index = 0
        self.current_hand_index = 0
        self.phase = Phase.BETTING
        self.bet_confirmed = [False for _ in range(self.num_players)]
        self.message = "Place bets, then press DEAL."

    """[Added]"""
    def confirm_bet(self, seat_index: int) -> None:
        if self.phase != Phase.BETTING:
            self.message = "Betting is not open."
            return

        if not (0 <= seat_index < self.num_players):
            return

        current_bet = self.player_bets[seat_index][0]

        if current_bet < self.DEFAULT_MIN_BET:
            self.message = f"{self.player_names[seat_index]} must enter a valid bet first."
            return

        if current_bet > self.player_balances[seat_index]:
            self.message = f"{self.player_names[seat_index]} does not have enough balance."
            return

        self.bet_confirmed[seat_index] = True

        waiting = [
            self.player_names[i]
            for i, done in enumerate(self.bet_confirmed)
            if not done
        ]

        if waiting:
            self.message = "Waiting for bet confirmation from: " + ", ".join(waiting)
        else:
            self.message = "All bets confirmed. Host can deal cards now."

    """[Added]"""
    def all_bets_confirmed(self) -> bool:
        return all(self.bet_confirmed)

    """[Added]"""
    def complete_betting_and_deal(self, bets: List[int]) -> None:
        if self.phase != Phase.BETTING:
            self.message = "You can only deal from the betting phase."
            return

        if len(bets) != self.num_players:
            self.message = "Invalid betting data."
            return

        normalized: List[int] = []
        for i, raw_bet in enumerate(bets):
            try:
                bet = int(raw_bet)
            except Exception:
                bet = self.DEFAULT_MIN_BET

            if bet < self.DEFAULT_MIN_BET:
                bet = self.DEFAULT_MIN_BET
            if bet > self.player_balances[i]:
                self.message = f"{self.player_names[i]} does not have enough balance."
                return
            normalized.append(bet)

        for i, bet in enumerate(normalized):
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
            self._advance_turn(initial_pass=True)
        

    def _initial_deal_all(self) -> None:
        for _ in range(2):
            for seat in self.players:
                seat[0].add(self.deck.draw())
            self.dealer.add(self.deck.draw())
    
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
            f"{self.player_names[self.current_player_index]} / "
            f"Hand {self.current_hand_index + 1}: choose an action."
        )

    """[Fixed]"""
    def _set_current_outcome(self, text: str) -> None:
        self.outcome_texts[self.current_player_index][self.current_hand_index] = text

    """[Added]"""
    def _all_hands_finished_or_blocked(self) -> bool:
        for seat in self.players:
            for hand in seat:
                if not hand.is_blackjack() and not hand.is_bust():
                    return False
        return True
    
    """[Added]"""
    def _advance_turn(self, initial_pass: bool = False) -> None:
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

                if outcome in ("STAND", "LOSE", "SURRENDER", "BLACKJACK"):
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
            if initial_pass:
                initial_pass = False
    
    """[Fixed]"""    
    def _evaluate_hand(self, player_hand: Hand, dealer_hand: Hand) -> str:
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
        if d_total > p_total:
            return "LOSE"
        return "PUSH"
        
    # ----------------------------
    # action guards
    # ----------------------------   

    def can_hit(self) -> bool:
        return self.phase == Phase.PLAYER_TURN and not self._current_hand().is_bust()
    
    def can_stand(self) -> bool:
        return self.phase == Phase.PLAYER_TURN and not self._current_hand().is_bust()
    
    def can_double_down(self) -> bool:
        if self.phase != Phase.PLAYER_TURN:
            return False
        hand = self._current_hand()
        balance = self.player_balances[self.current_player_index]
        bet = self._current_bet()
        return len(hand.cards) == 2 and not hand.is_bust() and balance >= bet

    def can_split(self) -> bool:
        if self.phase != Phase.PLAYER_TURN:
            return False
        hands = self.players[self.current_player_index]
        if len(hands) != 1:
            return False
        hand = hands[0]
        balance = self.player_balances[self.current_player_index]
        bet = self.player_bets[self.current_player_index][0]
        return (
            len(hand.cards) == 2
            and hand.cards[0].rank == hand.cards[1].rank
            and balance >= bet
        )
    
    def can_surrender(self) -> bool:
        if self.phase != Phase.PLAYER_TURN:
            return False
        return (
            len(self._current_hand().cards) == 2
            and self.outcome_texts[self.current_player_index][self.current_hand_index] == ""
        )

    # ----------------------------
    # player actions
    # ----------------------------

    def player_hit(self) -> None:
        if not self.can_hit():
            self.message = "HIT is not allowed right now."
            return
        hand = self._current_hand()
        hand.add(self.deck.draw())
        if hand.is_bust():
            self._set_current_outcome("LOSE")
            self.current_hand_index += 1
            self._advance_turn()
        else:
            self.message = f"{self.player_names[self.current_player_index]} hits ({hand.best_total()})."


    def player_stand(self) -> None:
        if not self.can_stand():
            self.message = "STAND is not allowed right now."
            return
        self._set_current_outcome("STAND")
        self.current_hand_index += 1
        self._advance_turn()


    def player_double_down(self) -> None:
        if not self.can_double_down():
            self.message = "DOUBLE is not allowed right now."
            return
        p = self.current_player_index
        h = self.current_hand_index
        extra = self.player_bets[p][h]
        self.player_balances[p] -= extra
        self.player_bets[p][h] += extra
        hand = self.players[p][h]
        hand.add(self.deck.draw())
        self.outcome_texts[p][h] = "LOSE" if hand.is_bust() else "STAND"
        self.current_hand_index += 1
        self._advance_turn()

    def player_surrender(self) -> None:
        if not self.can_surrender():
            self.message = "SURRENDER is not allowed right now."
            return
        p = self.current_player_index
        h = self.current_hand_index
        refund = self.player_bets[p][h] // 2
        self.player_balances[p] += refund
        self.outcome_texts[p][h] = "SURRENDER"
        self.current_hand_index += 1
        self._advance_turn()


    def player_split(self) -> None:
        if not self.can_split():
            self.message = "SPLIT is not allowed right now."
            return
        p = self.current_player_index
        h = self.current_hand_index
        current_hand = self.players[p][h]
        original_bet = self.player_bets[p][h]

        new_hand = Hand()
        moved_card = current_hand.cards.pop()
        new_hand.add(moved_card)

        current_hand.add(self.deck.draw())
        new_hand.add(self.deck.draw())

        self.players[p].insert(h + 1, new_hand)
        self.player_bets[p].insert(h + 1, original_bet)
        self.outcome_texts[p].insert(h + 1, "")
        self.player_balances[p] -= original_bet
        self.message = self._turn_message()

        
    # ----------------------------
    # dealer + resolve 
    # ----------------------------

    def run_dealer_turn(self) -> None:
        while self.dealer.best_total() < 17:
            self.dealer.add(self.deck.draw())
        

    def resolve_round(self) -> None:
        summary = [f"Dealer: {self.dealer.best_total()}"]
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
                    self.player_balances[p] += int(bet * (1 + self.BLACKJACK_PAYOUT))
                elif result == "WIN":
                    self.player_balances[p] += bet * 2
                elif result == "PUSH":
                    self.player_balances[p] += bet
                summary.append(f"{self.player_names[p]}-H{h + 1}:{result}")

        self.phase = Phase.ROUND_OVER
        self.message = " | ".join(summary)

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
