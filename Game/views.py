from django.shortcuts import render, redirect
from .engine import GameEngine
from . import engine_api


def clear_session(request):
    """
    Clear all game-related keys.
    """
    request.session.flush()
    return redirect("blackjack_home")


def blackjack_game(request):
    """
    GET:
      - If no session state -> show START screen
      - If session exists -> render current game view_state
    POST:
      - START -> create engine + NEW round immediately
      - HIT/STAND/NEW -> restore engine, apply action, save, render
    """

    # 1) Restore engine from session (if exists)
    raw_state = request.session.get(engine_api.SESSION_KEY_ENGINE_STATE)
    engine = engine_api.import_state(raw_state) if raw_state else None

    # 2) Handle actions
    if request.method == "POST":
        action = (request.POST.get("action") or "").upper().strip()

        # QUIT 
        if action == "START":
            request.session.flush()
            return redirect("blackjack_home")
        try:
            user_bet = int(request.POST.get("bet_amount", 100))
        except (ValueError, TypeError):
            user_bet = 100
        
        if engine is None:
            if action == engine_api.ACTION_NEW: 
                engine = GameEngine()
                engine_api.apply_action(engine, engine_api.ACTION_NEW, user_bet)
        else:
        
            allowed_actions = (
                engine_api.ACTION_NEW, 
                engine_api.ACTION_HIT, 
                engine_api.ACTION_STAND,
                engine_api.ACTION_DOUBLE,
                engine_api.ACTION_SPLIT,
                "SURRENDER"
            )

            if action in allowed_actions:
                engine_api.apply_action(engine, action, user_bet)
            
        if engine:
            request.session[engine_api.SESSION_KEY_ENGINE_STATE] = engine_api.export_state(engine)
            request.session.modified = True

        return redirect("blackjack_home")

    # 3) Render
    if engine is None:
        return render(request, "UI.html", {"started": False})
    
    context = engine_api.get_view_state(engine)
    return render(request, "UI.html", {"state": context, "started": True})