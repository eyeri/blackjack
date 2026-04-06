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
ACTION_DEAL = "DEAL"
ACTION_JOIN = "JOIN"
ACTION_READY = "READY"
ACTION_CONFIRM_BET = "CONFIRM_BET"

# milestone 5 [added]
ACTION_TAKE_INSURANCE = "TAKE_INSURANCE"
ACTION_SKIP_INSURANCE = "SKIP_INSURANCE"

ACTION_TUTORIAL = "START_TUTORIAL" 

SESSION_KEY_ENGINE_STATE = "engine_state"

def card_to_code(card: Card) -> str:
    return card.code()

def code_to_card(code: str) -> Card:
    return Card(rank=code[:-1], suit=code[-1])

def hand_to_codes(hand: Hand) -> List[str]:
    return [card_to_code(c) for c in hand.cards]

def codes_to_hand(codes: List[str]) -> Hand:
    hand = Hand()
    for code in codes:
        hand.add(code_to_card(code))
    return hand

def deck_to_codes(deck: Deck) -> List[str]:
    return [card_to_code(c) for c in deck.cards]

def codes_to_deck(codes: List[str]) -> Deck:
    deck = Deck.__new__(Deck)
    deck.cards = [code_to_card(c) for c in codes]
    return deck


# Export / Import (Session State)


def export_state(engine: GameEngine) -> Dict[str, Any]:
    return {
        "num_players": engine.num_players,
        "is_tutorial": engine.is_tutorial,
        "deck": deck_to_codes(engine.deck),
        "dealer_cards": hand_to_codes(engine.dealer),
        "players": [[hand_to_codes(hand) for hand in seat] for seat in engine.players],
        "player_bets": engine.player_bets,
        "player_balances": engine.player_balances,
        "outcome_texts": engine.outcome_texts,
        "player_names": engine.player_names,
        "player_ready": engine.player_ready,
        "bet_confirmed": engine.bet_confirmed,

        # milestone 5 [added]
        "insurance_bets": engine.insurance_bets,
        "insurance_decided": engine.insurance_decided,

        "current_player_index": engine.current_player_index,
        "current_hand_index": engine.current_hand_index,
        "phase": engine.phase.name,
        "message": engine.message,
        "tutorial_message": engine.tutorial_message,
    }


def import_state(state_dict: Optional[Dict[str, Any]]) -> Optional[GameEngine]:
    if not state_dict:
        return None

    engine = GameEngine(
        num_players=state_dict.get("num_players", 2),
        is_tutorial=state_dict.get("is_tutorial", False),
    )
    engine.deck = codes_to_deck(state_dict["deck"])
    engine.dealer = codes_to_hand(state_dict["dealer_cards"])
    engine.players = [
        [codes_to_hand(hand_codes) for hand_codes in seat]
        for seat in state_dict["players"]
    ]
    engine.player_bets = state_dict["player_bets"]
    engine.player_balances = state_dict["player_balances"]
    engine.outcome_texts = state_dict["outcome_texts"]
    engine.player_names = state_dict.get(
        "player_names", [f"Player {i + 1}" for i in range(engine.num_players)]
    )
    engine.player_ready = state_dict.get(
        "player_ready", [True for _ in range(engine.num_players)]
    )
    engine.current_player_index = state_dict.get("current_player_index", 0)
    engine.current_hand_index = state_dict.get("current_hand_index", 0)
    engine.bet_confirmed = state_dict.get(
        "bet_confirmed", [False for _ in range(engine.num_players)]
    )

    # milestone 5 [fixed]
    engine.insurance_bets = state_dict.get(
        "insurance_bets", [0 for _ in range(engine.num_players)]
    )
    engine.insurance_decided = state_dict.get(
        "insurance_decided", [False for _ in range(engine.num_players)]
    )

    engine.phase = Phase[state_dict.get("phase", "WAITING")]
    engine.message = state_dict.get("message", "")
    engine.tutorial_message = state_dict.get("tutorial_message", "")
    return engine


def apply_action(engine: GameEngine, action: str, bet: int = 100) -> None:
    if action == ACTION_NEW:
        engine.start_betting_round()
    elif action == ACTION_HIT:
        engine.player_hit()
    elif action == ACTION_STAND:
        engine.player_stand()
    elif action == ACTION_DOUBLE:
        engine.player_double_down()
    elif action == ACTION_SPLIT:
        engine.player_split()
    elif action == ACTION_SURRENDER:
        engine.player_surrender()

def _dealer_display(engine: GameEngine, viewer_is_player: bool = True) -> tuple[list[str], Optional[int]]:
    dealer_codes = engine.dealer.codes()

    if viewer_is_player and engine.phase in (Phase.PLAYER_TURN, Phase.INSURANCE) and len(dealer_codes) >= 2:
        return ["??"] + dealer_codes[1:], None

    return dealer_codes, engine.dealer.best_total() if engine.dealer.cards else None


def _mask_other_player_hand(hand: Hand, show_real_cards: bool) -> List[str]:
    if show_real_cards:
        return hand.codes()
    return ["??" for _ in hand.cards]

def get_view_state_for_player(engine: GameEngine, viewer_index: int, table_code: str) -> Dict[str, Any]:
    dealer_cards, dealer_total = _dealer_display(engine, viewer_is_player=True)
    players_state = []

    for i, seat in enumerate(engine.players):
        hand_states = []
        viewer_is_self = i == viewer_index

        for j, hand in enumerate(seat):
            is_turn = (
                engine.phase == Phase.PLAYER_TURN
                and i == engine.current_player_index
                and j == engine.current_hand_index
            )

            hand_states.append(
                {
                    "cards": _mask_other_player_hand(
                        hand,
                        viewer_is_self or engine.phase == Phase.ROUND_OVER
                    ),
                    "total": hand.best_total()
                    if (viewer_is_self or engine.phase == Phase.ROUND_OVER) and hand.cards
                    else None,
                    "bet": engine.player_bets[i][j],
                    "outcome": engine.outcome_texts[i][j]
                    if engine.phase == Phase.ROUND_OVER or viewer_is_self
                    else "",
                    "is_turn": is_turn,
                    "can_act": viewer_is_self and is_turn,
                    "is_owner": viewer_is_self,
                }
            )

        players_state.append(
            {
                "label": engine.player_names[i],
                "balance": engine.player_balances[i],
                "hands": hand_states,
                "bet_confirmed": engine.bet_confirmed[i],
                "bet_value": engine.player_bets[i][0],
                "is_active": engine.phase == Phase.PLAYER_TURN and i == engine.current_player_index,
                "is_owner": viewer_is_self,
                "ready": engine.player_ready[i],

                # [M5] player insurance
                "insurance_bet": engine.insurance_bets[i],
                "insurance_decided": engine.insurance_decided[i],
            }
        )

    return {
        "table_code": table_code,
        "phase": engine.phase.name,
        "message": engine.message,
        "is_tutorial": engine.is_tutorial,
        "tutorial_message": engine.tutorial_message,
        "advice": engine.get_advice()
        if engine.is_tutorial and viewer_index == engine.current_player_index
        else "",
        "dealer_cards": dealer_cards,
        "dealer_total": dealer_total,
        "players": players_state,
        "viewer_index": viewer_index,
        "viewer_name": engine.player_names[viewer_index],

        # [M5] viewer: insurance information
        "insurance": {
            "offered": engine.phase == Phase.INSURANCE,
            "amount": engine.player_bets[viewer_index][0] // 2 if engine.phase == Phase.INSURANCE else 0,
            "decided": engine.insurance_decided[viewer_index] if engine.phase == Phase.INSURANCE else False,
            "taken": engine.insurance_bets[viewer_index] > 0 if engine.phase in (Phase.INSURANCE, Phase.ROUND_OVER) else False,
        },

        "buttons": {
            "start_round": engine.phase in (Phase.WAITING, Phase.ROUND_OVER),
            "deal": engine.phase == Phase.BETTING and engine.all_bets_confirmed(),
            "hit": viewer_index == engine.current_player_index and engine.can_hit(),
            "stand": viewer_index == engine.current_player_index and engine.can_stand(),
            "double": viewer_index == engine.current_player_index and engine.can_double_down(),
            "split": viewer_index == engine.current_player_index and engine.can_split(),
            "surrender": viewer_index == engine.current_player_index and engine.can_surrender(),
            "confirm_bet": engine.phase == Phase.BETTING and not engine.bet_confirmed[viewer_index],

            # [M5] insurance
            "take_insurance": engine.can_take_insurance(viewer_index),
            "skip_insurance": engine.phase == Phase.INSURANCE and not engine.insurance_decided[viewer_index],
        },
    }