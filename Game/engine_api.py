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
        "phase": engine.phase.name,
        "message": engine.message,
        "outcome_text": getattr(engine, "outcome_text", ""),
        "player_cards": hand_to_codes(engine.player),
        "dealer_cards": hand_to_codes(engine.dealer),
        "deck_cards": deck_to_codes(engine.deck),
    }

def import_state(data: Dict[str, Any]) -> GameEngine:
    """
    Restore engine from a session dict.
    Must NOT introduce randomness here.
    """
    g = GameEngine()

    # restore phase/message/outcome
    g.phase = Phase[data["phase"]]
    g.message = data.get("message", "")
    g.outcome_text = data.get("outcome_text", "")

    # restore hands & deck
    g.player = codes_to_hand(data.get("player_cards", []))
    g.dealer = codes_to_hand(data.get("dealer_cards", []))
    g.deck = codes_to_deck(data.get("deck_cards", []))

    return g


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

def apply_action(engine, action: str) -> None:
    """
    Thin dispatcher: UI action -> engine method call only.
    No learning logic. No rules beyond phase gating.
    """
    act = (action or "").upper().strip()

    if act == ACTION_NEW:
        engine.new_round()
        return

    if engine.phase != Phase.PLAYER_TURN:
        return

    if act == ACTION_HIT:
        engine.player_hit()
        return

    if act == ACTION_STAND:
        engine.player_stand()
        return

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

def get_view_state(engine, hide_dealer_hole: bool = True) -> dict[str, Any]:
    """
    Render model only (data for UI).
    Must not mutate engine. Must not contain tutorial/trainer logic.
    """
    # TODO: read phase
    current_phase: str = engine.phase

    action_hit: bool = (current_phase == Phase.PLAYER_TURN)
    action_stand: bool = (current_phase == Phase.PLAYER_TURN)
    action_new: bool = True # can reset whenever you want



    # TODO: compute player_total, dealer_total
    player_total: int = engine.player.best_total()
    dealer_total: int = engine.dealer.best_total()

    # TODO: get card codes for player/dealer
    dealer_cards: List[str] = hand_to_codes(engine.dealer)
    player_cards: List[str] = hand_to_codes(engine.player)
    


    # TODO: hide dealer hole card if PLAYER_TURN
    if (hide_dealer_hole and (engine.phase == Phase.PLAYER_TURN)):
        dealer_cards = ["??"] + dealer_cards[1:]
        dealer_total = None


    buttons = {
        "hit":  action_hit,  # TODO: phase-based
        "stand": action_stand, # TODO: phase-based
        "new":  action_new,   # You decided: NEW available without refresh
    }

    return {
        "phase": engine.phase.name,
        "message": engine.message,   # TODO: engine message if exists
        "outcome": getattr(engine, "outcome_text", ""),   # TODO: outcome text if exists
        "player_cards": player_cards,
        "dealer_cards": dealer_cards,
        "player_total": player_total,
        "dealer_total": dealer_total,
        "buttons": buttons,
    }