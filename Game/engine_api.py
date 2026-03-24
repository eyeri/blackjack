from __future__ import annotations
from typing import Dict, Any, List, Optional

try:
    from .engine import GameEngine, Phase
    from .card import Card
    from .deck import Deck
    from .hand import Hand
except Exception:
    from engine import GameEngine, Phase
    from card import Card
    from deck import Deck
    from hand import Hand

ACTION_START = "START"
ACTION_NEW   = "NEW"
ACTION_HIT   = "HIT"
ACTION_STAND = "STAND"
ACTION_DOUBLE = "DOUBLE"
ACTION_SPLIT = "SPLIT"
ACTION_SURRENDER = "SURRENDER"
ACTION_DEAL = "DEAL" # milestone 4
ACTION_TUTORIAL = "START_TUTORIAL" # milestone 4

SESSION_KEY_ENGINE_STATE = "engine_state"

def card_to_code(card: Card) -> str:
    return card.code()

def code_to_card(code: str) -> Card:
    suit = code[-1]
    rank = code[:-1]
    return Card(rank=rank, suit=suit)

def hand_to_codes(hand: Hand) -> List[str]:
    return [card_to_code(c) for c in hand.cards]

def codes_to_hand(codes: List[str]) -> Hand:
    h = Hand()
    for code in codes:
        h.add(code_to_card(code))
    return h

def deck_to_codes(deck: Deck) -> List[str]:
    return [card_to_code(c) for c in deck.cards]

def codes_to_deck(codes: List[str]) -> Deck:
    d = Deck.__new__(Deck) 
    d.cards = [code_to_card(c) for c in codes]
    return d


# Export / Import (Session State)

"""[Fixed]"""
def export_state(engine: GameEngine) -> Dict[str, Any]:
    return {
        "num_players": engine.num_players,
        "is_tutorial": engine.is_tutorial,
        "deck": deck_to_codes(engine.deck),
        "dealer_cards": hand_to_codes(engine.dealer),
        "players": [
            [hand_to_codes(hand) for hand in seat]
            for seat in engine.players
        ],
        "player_bets": engine.player_bets,
        "player_balances": engine.player_balances,
        "outcome_texts": engine.outcome_texts,
        "current_player_index": engine.current_player_index,
        "current_hand_index": engine.current_hand_index,
        "phase": engine.phase.name,
        "message": engine.message,
        "tutorial_message": engine.tutorial_message,
    }

"""[Added]"""
def _validate_restored_engine(engine: GameEngine) -> None:
        """
        Defensive validation after session restore.
        Fails early if the restored object graph is wrong.
        """
        if not isinstance(engine.dealer, Hand):
            raise TypeError("Restored dealer is not a Hand instance.")

        if not isinstance(engine.players, list):
            raise TypeError("Restored players must be a list.")

        if len(engine.players) != engine.num_players:
            raise ValueError("Restored players length does not match num_players.")

        for p, seat in enumerate(engine.players):
            if not isinstance(seat, list):
                raise TypeError(f"Player {p} seat is not a list of hands.")
            if len(seat) == 0:
                raise ValueError(f"Player {p} has no hands after restore.")

            for h, hand in enumerate(seat):
                if not isinstance(hand, Hand):
                    raise TypeError(f"Player {p} hand {h} is not a Hand instance.")

        if len(engine.player_bets) != engine.num_players:
            raise ValueError("player_bets length mismatch.")
        if len(engine.player_balances) != engine.num_players:
            raise ValueError("player_balances length mismatch.")
        if len(engine.outcome_texts) != engine.num_players:
            raise ValueError("outcome_texts length mismatch.")

"""[Fixed]"""
def import_state(state_dict: Optional[Dict[str, Any]]) -> Optional[GameEngine]:
    if not state_dict:
        return None

    engine = GameEngine(
        num_players=state_dict.get("num_players", 1),
        is_tutorial=state_dict.get("is_tutorial", False),
    )

    # restore deterministic deck / dealer
    engine.deck = codes_to_deck(state_dict["deck"])
    engine.dealer = codes_to_hand(state_dict["dealer_cards"])

    # restore players -> each seat is a list of Hand objects
    engine.players = [
        [codes_to_hand(hand_codes) for hand_codes in seat]
        for seat in state_dict["players"]
    ]

    engine.player_bets = state_dict["player_bets"]
    engine.player_balances = state_dict["player_balances"]
    engine.outcome_texts = state_dict["outcome_texts"]

    engine.current_player_index = state_dict.get("current_player_index", 0)
    engine.current_hand_index = state_dict.get("current_hand_index", 0)

    engine.phase = Phase[state_dict["phase"]]
    engine.message = state_dict.get("message", "")
    engine.tutorial_message = state_dict.get("tutorial_message", "")

    _validate_restored_engine(engine)
    return engine


"""[Fixed]"""
def apply_action(engine: GameEngine, action: str) -> None:
    action = (action or "").upper().strip()

    if action == ACTION_HIT:
        engine.player_hit()
    elif action == ACTION_STAND:
        engine.player_stand()
    elif action == ACTION_DOUBLE:
        engine.player_double_down()
    elif action == ACTION_SPLIT:
        engine.player_split()
    elif action == ACTION_SURRENDER:
        engine.player_surrender()

"""[Fixed]"""
def get_view_state(engine: GameEngine) -> Dict[str, Any]:
    dealer_codes = engine.dealer.codes()

    if engine.phase == Phase.PLAYER_TURN and len(dealer_codes) >= 2:
        dealer_display = ["??"] + dealer_codes[1:]
        dealer_total = None
    else:
        dealer_display = dealer_codes
        dealer_total = engine.dealer.best_total() if engine.dealer.cards else None

    players_state = []
    for i, seat in enumerate(engine.players):
        hand_states = []
        for j, hand in enumerate(seat):
            is_turn = (
                engine.phase == Phase.PLAYER_TURN
                and i == engine.current_player_index
                and j == engine.current_hand_index
            )
            hand_states.append({
                "cards": hand.codes(),
                "total": hand.best_total() if hand.cards else None,
                "bet": engine.player_bets[i][j],
                "outcome": engine.outcome_texts[i][j],
                "is_turn": is_turn,
                "can_act": is_turn,
            })

        players_state.append({
            "label": f"Player {i + 1}",
            "balance": engine.player_balances[i],
            "hands": hand_states,
        })

    return {
        "phase": engine.phase.name,
        "message": engine.message,
        "is_tutorial": engine.is_tutorial,
        "tutorial_message": engine.tutorial_message,
        "advice": engine.get_advice() if engine.is_tutorial else "",
        "num_players": engine.num_players,
        "dealer_cards": dealer_display,
        "dealer_total": dealer_total,
        "players": players_state,
        "buttons": {
            "hit": engine.can_hit(),
            "stand": engine.can_stand(),
            "double": engine.can_double_down(),
            "split": engine.can_split(),
            "surrender": engine.can_surrender(),
            "deal": engine.phase == Phase.BETTING,
            "new_round": engine.phase in (Phase.INIT, Phase.BETTING, Phase.ROUND_OVER),
        },
    }