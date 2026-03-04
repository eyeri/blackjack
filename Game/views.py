from django.shortcuts import render, redirect

from .engine import GameEngine, Phase
from .card import Card


def _clear_game_session(request):
    for k in ("started", "locked", "game_state", "deck_serialized", "message", "preserve_once"):
        if k in request.session:
            del request.session[k]
    request.session.modified = True


def _init_new_game(request):
    engine = GameEngine()
    engine.new_round()

    request.session["started"] = True
    request.session["locked"] = False
    request.session["game_state"] = engine.state_snapshot(hide_dealer_hole=True)
    request.session["deck_serialized"] = [c.code() for c in engine.deck.cards]
    request.session["message"] = "Game started. Choose HIT or STAND (only one action allowed)."
    request.session["preserve_once"] = True
    request.session.modified = True


def _restore_engine_from_session(state, deck_codes):
    engine = GameEngine()

    engine.player.cards = [Card(rank=c[:-1], suit=c[-1]) for c in state.get("player_cards", [])]
    engine.dealer.cards = [
        Card(rank=c[:-1], suit=c[-1])
        for c in state.get("dealer_cards", [])
        if c != "??"
    ]

    engine.deck.cards = [Card(rank=c[:-1], suit=c[-1]) for c in deck_codes]
    engine.phase = Phase[state.get("phase", "PLAYER_TURN")]

    return engine


def blackjack_game(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "start":
            _init_new_game(request)
            return redirect("blackjack_home")

        started = bool(request.session.get("started", False))
        locked = bool(request.session.get("locked", False))
        state = request.session.get("game_state")
        deck_codes = request.session.get("deck_serialized", [])

        if (not started) or (not state) or locked:
            request.session["preserve_once"] = True
            request.session.modified = True
            return redirect("blackjack_home")

        engine = _restore_engine_from_session(state, deck_codes)

        if action == "hit":
            engine.player_hit()

            if engine.phase != Phase.ROUND_OVER:
                engine.phase = Phase.DEALER_TURN
                engine.run_dealer_turn()
                engine.resolve_round()

            engine.message = "HIT done. Dealer played. Buttons locked. Press F5 to reset."
            engine.phase = Phase.ROUND_OVER

        elif action == "stand":
            engine.player_stand()

            engine.message = "STAND done. Dealer played. Buttons locked. Press F5 to reset."
            engine.phase = Phase.ROUND_OVER

        request.session["locked"] = True
        request.session["game_state"] = engine.state_snapshot(hide_dealer_hole=False)  # 라운드 끝났으니 공개
        request.session["deck_serialized"] = [c.code() for c in engine.deck.cards]
        request.session["message"] = engine.message
        request.session["preserve_once"] = True
        request.session.modified = True

        return redirect("blackjack_home")

    preserve_once = bool(request.session.get("preserve_once", False))

    
    if preserve_once:
        request.session["preserve_once"] = False
        request.session.modified = True

        started = bool(request.session.get("started", False))
        if not started:
            return render(request, "UI.html", {"started": False})

        state = request.session.get("game_state")
        if not state:
            _clear_game_session(request)
            return render(request, "UI.html", {"started": False})

        return render(request, "UI.html", {
            "started": True,
            "state": state,
            "phase": state.get("phase", "INIT"),
            "message": request.session.get("message", ""),
            "locked": bool(request.session.get("locked", False)),
        })

    _clear_game_session(request)
    return render(request, "UI.html", {"started": False})