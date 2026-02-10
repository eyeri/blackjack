# engine_api.py (FIXED)
# Contract layer between Django UI and Pure-Python Game Engine
# Milestone 2: session-based state (JSON-serializable dict)
#
# FIX: Ensure import_state() never introduces randomness.
#      We rebuild Deck WITHOUT calling Deck() constructor (which may shuffle).

from __future__ import annotations
from typing import Dict, Any, List, Optional

# ---- Import compatibility (package vs script) ----
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


# ----------------------------
# Serialization helpers
# ----------------------------

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


# ----------------------------
# FIXED: Deck restore (NO shuffle, NO randomness)
# ----------------------------

def codes_to_deck(codes: List[str]) -> Deck:
    """
    Rebuild deck WITHOUT calling Deck() constructor.
    This prevents any accidental shuffle/randomness during session restore.
    """
    d = Deck.__new__(Deck)      # bypass __init__()
    d.cards = [code_to_card(c) for c in codes]
    return d


# ----------------------------
# Export / Import (Session State)
# ----------------------------

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


# ----------------------------
# Actions (UI calls only these)
# ----------------------------

def apply_action(engine: GameEngine, action: str) -> None:
    """
    Valid actions:
      - 'NEW'   : start a new round
      - 'HIT'   : player hit
      - 'STAND' : player stand (triggers dealer turn + resolve)
    """
    action = action.upper().strip()

    if action == "NEW":
        engine.new_round()
        return
    if action == "HIT":
        engine.player_hit()
        return
    if action == "STAND":
        engine.player_stand()
        return

    raise ValueError(f"Invalid action: {action}")


# ----------------------------
# UI View Model (Render Data)
# ----------------------------

def get_view_state(engine: GameEngine, hide_dealer_hole: bool = True) -> Dict[str, Any]:
    """
    UI-friendly dict for rendering.
    Django templates should render ONLY this data.
    """
    dealer_codes = hand_to_codes(engine.dealer)
    dealer_total: Optional[int] = engine.dealer.best_total()

    # Hide dealer hole card during player turn
    if hide_dealer_hole and engine.phase == Phase.PLAYER_TURN and len(dealer_codes) > 0:
        dealer_codes = ["??"] + dealer_codes[1:]
        dealer_total = None

    hit_enabled = (engine.phase == Phase.PLAYER_TURN)
    stand_enabled = (engine.phase == Phase.PLAYER_TURN)
    new_enabled = (engine.phase in (Phase.INIT, Phase.ROUND_OVER))

    return {
        "phase": engine.phase.name,
        "message": engine.message,
        "outcome": getattr(engine, "outcome_text", ""),
        "player_cards": hand_to_codes(engine.player),
        "dealer_cards": dealer_codes,
        "player_total": engine.player.best_total(),
        "dealer_total": dealer_total,
        "buttons": {
            "hit": hit_enabled,
            "stand": stand_enabled,
            "new": new_enabled,
        }
    }
