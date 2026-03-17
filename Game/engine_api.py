# ===================== CHANGES (Milestone 2 -> Game-focused Milestone 3) =====================
# 1) engine_api is the ONLY place for session serialization:
#    - export_state(engine) produces JSON-serializable dict for Django session /
#    - import_state(dict) restores engine WITHOUT introducing randomness /
#
# 2) Introduced (or standardized) constants for clarity and to avoid magic strings:
#    - ACTION_START / ACTION_NEW / ACTION_HIT / ACTION_STAND /
#    - SESSION_KEY_ENGINE_STATE = "engine_state" /
#
# 3) apply_action() policy hardened for web safety:
#    - Optional: ignore invalid actions instead of raising ValueError (prevents request crash) / 
#    - Optional: allow HIT/STAND only during Phase.PLAYER_TURN (prevents illegal transitions) / 
#
# 4) get_view_state() is a pure "render model":----------------------------
#    - It must NOT contain learning/trainer logic.
#    - It can hide dealer hole card during PLAYER_TURN ("??")
#    - It can provide button enable/disable states derived from engine.phase
#
# 5) NEW button policy moved to view_state:
#    - BEFORE : NEW enabled only in INIT or ROUND_OVER
#    - AFTER  : NEW can be enabled during the round (no F5 reset required),
#            if we want "Start next round anytime" behavior.
# =============================================================================================
from __future__ import annotations
from typing import Dict, Any, List, Optional

# Import compatibility (package vs script)
try:
    # when used as a package: from blackjack.engine_api import ...
    from .engine import GameEngine, Phase
    from .card import Card
    from .deck import Deck
    from .hand import Hand
except Exception:
    # when run locally as plain files
    from engine import GameEngine, Phase
    from card import Card
    from deck import Deck
    from hand import Hand

# UI action constants 
ACTION_START = "START"
ACTION_NEW   = "NEW"
ACTION_HIT   = "HIT"
ACTION_STAND = "STAND"
ACTION_DOUBLE = "DOUBLE"
ACTION_SPLIT = "SPLIT"
ACTION_SURRENDER = "SURRENDER"

# Session key
SESSION_KEY_ENGINE_STATE = "engine_state"

# Serialization helpers

def card_to_code(card: Card) -> str:
    """Serialize Card -> ASCII code like 'AS', '10H', 'KD'."""
    return card.code()

def code_to_card(code: str) -> Card:
    """
    Deserialize ASCII code -> Card.
    Code format: rank + suit, e.g. 'AS', '10H', 'KD', '7C'
    """
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
    """
    Serialize remaining deck order so the game is deterministic across requests.
    Assumes Deck keeps remaining cards in `deck.cards` in draw order.
    """
    return [card_to_code(c) for c in deck.cards]


# Deck restore (NO shuffle, NO randomness)

def codes_to_deck(codes: List[str]) -> Deck:
    """
    Rebuild deck WITHOUT calling Deck() constructor.
    This prevents any accidental shuffle/randomness during session restore.
    """
    d = Deck.__new__(Deck)      # bypass __init__()
    d.cards = [code_to_card(c) for c in codes]
    return d


# Export / Import (Session State)

def export_state(engine: GameEngine) -> Dict[str, Any]:
    """
    Convert engine into a JSON-serializable dict for Django session.
    No objects allowed in returned dict.
    """
    return {
        "deck": [card.code() if hasattr(card, 'code') and callable(card.code) else card.code for card in engine.deck.cards],
        "player_cards": engine.player.codes(),
        "dealer_cards": engine.dealer.codes(),
        "second_hand_cards": engine.second_hand.codes(), 
        "phase": engine.phase.name,
        "message": engine.message,
        "player_balance": engine.player_balance,         
        "current_bet": engine.current_bet,
        "hand_bets": engine.hand_bets,                   
        "outcome_texts": engine.outcome_texts
    }

def import_state(state_dict: Dict[str, Any]) -> GameEngine:
    """
    Restore engine from a session dict.
    Must NOT introduce randomness here.
    """
    if not state_dict: return None
    engine = GameEngine()
    # restore hands & deck
    engine.deck = codes_to_deck(state_dict["deck"])
    engine.player = codes_to_hand(state_dict["player_cards"])
    engine.dealer = codes_to_hand(state_dict["dealer_cards"])
    engine.second_hand = codes_to_hand(state_dict.get("second_hand_cards", []))

    # restore phase/message/outcome
    engine.phase = Phase[state_dict["phase"]]
    engine.message = state_dict["message"]

    balance_val = state_dict.get("player_balance", 1000)
    if hasattr(engine, 'player_balance') and not callable(engine.player_balance):
        engine.player_balance = balance_val
        
    engine.current_bet = state_dict.get("current_bet", 0)
    engine.hand_bets = state_dict.get("hand_bets", {"player": 0, "second_hand": 0})
    engine.outcome_texts = state_dict.get("outcome_texts", {})

    return engine


# Actions (UI calls only these) [Old Version]
# 
# def apply_action(engine: GameEngine, action: str) -> None:
#     """
#     Valid actions:
#       - 'NEW'   : start a new round
#       - 'HIT'   : player hit
#       - 'STAND' : player stand (triggers dealer turn + resolve)
#     """
#     action = action.upper().strip()
# 
#     if action == "NEW":
#         engine.new_round()
#         return
#     if action == "HIT":
#         engine.player_hit()
#         return
#     if action == "STAND":
#         engine.player_stand()
#         return
# 
#     raise ValueError(f"Invalid action: {action}")

# === !!!ADD/REPLACE apply_action skeleton!!! ===

def apply_action(engine: GameEngine, action: str, bet_amount: int = 100):
    action = action.upper()
    """
    Thin dispatcher: UI action -> engine method call only.
    No learning logic. No rules beyond phase gating.
    """
    action = action.upper().strip()

    if action == ACTION_NEW:
        engine.new_round(bet_amount)

    elif action == ACTION_HIT: 
        engine.player_hit()

    elif action == ACTION_STAND: 
        engine.player_stand()

    elif action == ACTION_DOUBLE: 
        engine.player_double_down() 

    elif action == ACTION_SURRENDER:
        engine.player_surrender()

    elif action == ACTION_NEW:
        engine.new_round(bet_amount)

    elif action == ACTION_SPLIT: 
        engine.player_split()

    # Unknown action -> ignore


# UI View Model (Render Data) [Old Version]
# 
# def get_view_state(engine: GameEngine, hide_dealer_hole: bool = True) -> Dict[str, Any]:
#     """
#     UI-friendly dict for rendering.
#     Django templates should render ONLY this data.
#     """
#     dealer_codes = hand_to_codes(engine.dealer)
#     dealer_total: Optional[int] = engine.dealer.best_total()
# 
#     # Hide dealer hole card during player turn
#     if hide_dealer_hole and engine.phase == Phase.PLAYER_TURN and len(dealer_codes) > 0:
#         dealer_codes = ["??"] + dealer_codes[1:]
#         dealer_total = None
# 
#     hit_enabled = (engine.phase == Phase.PLAYER_TURN)
#     stand_enabled = (engine.phase == Phase.PLAYER_TURN)
#     new_enabled = (engine.phase in (Phase.INIT, Phase.ROUND_OVER))
# 
#     return {
#         "phase": engine.phase.name,
#         "message": engine.message,
#         "outcome": getattr(engine, "outcome_text", ""),
#         "player_cards": hand_to_codes(engine.player),
#         "dealer_cards": dealer_codes,
#         "player_total": engine.player.best_total(),
#         "dealer_total": dealer_total,
#         "buttons": {
#             "hit": hit_enabled,
#             "stand": stand_enabled,
#             "new": new_enabled,
#         }
#     }

# === !!!ADD/REPLACE get_view_state skeleton!!! ===


# 4) get_view_state() is a pure "render model":----------------------------
#    - It must NOT contain learning/trainer logic.
#    - It can hide dealer hole card during PLAYER_TURN ("??")
#    - It can provide button enable/disable states derived from engine.phase

def get_view_state(engine: GameEngine) -> Dict[str, Any]:
    """
    Render model only (data for UI).
    Must not mutate engine. Must not contain tutorial/trainer logic.
    """
    dealer_display = engine.dealer.codes()
    if engine.phase == Phase.PLAYER_TURN:
        dealer_display = ["??"] + dealer_display[1:]
        dealer_total = None
    else:
        dealer_total = engine.dealer.best_total()
    
    return {
        "phase": engine.phase.name,
        "message": engine.message,
        "player_cards": engine.player.codes(),
        "dealer_cards": dealer_display,
        "second_hand_cards": engine.second_hand.codes(), 
        "player_total": engine.player.best_total(),
        "second_hand_total": engine.second_hand.best_total() if engine.second_hand.cards else None,
        "dealer_total": dealer_total,
        
        
        "player_balance": engine.player_balance,  
        "current_bet": engine.current_bet,        
        
        "outcome_texts": engine.outcome_texts,
        "buttons": {
            "hit": engine.phase == Phase.PLAYER_TURN,
            "stand": engine.phase == Phase.PLAYER_TURN,
            "double": engine.can_double_down(),   
            "split": engine.can_split(),         
            "new": True
        }
    }