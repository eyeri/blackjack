from __future__ import annotations

import random
import string
import json
from typing import List
from django.http import JsonResponse
from django.db import transaction
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from . import engine_api
from .engine import GameEngine, Phase
from .models import GameTable, TableParticipant

TUTORIAL_SESSION_KEY = "tutorial_engine_state"


def _load_tutorial_engine(request: HttpRequest) -> GameEngine:
    raw_state = request.session.get(TUTORIAL_SESSION_KEY)
    engine = engine_api.import_state(raw_state) if raw_state else None
    if engine is None:
        engine = GameEngine(num_players=1, is_tutorial=True)
        engine.set_player_name(0, "Tutorial Player")
        engine.set_player_ready(0, True)
        engine.message = "Welcome to Tutorial Mode."
    return engine


def _save_tutorial_engine(request: HttpRequest, engine: GameEngine) -> None:
    request.session[TUTORIAL_SESSION_KEY] = engine_api.export_state(engine)
    request.session.modified = True


@require_http_methods(["GET", "POST"])
def tutorial(request: HttpRequest) -> HttpResponse:
    engine = _load_tutorial_engine(request)

    if request.method == "POST":
        action = (request.POST.get("action") or "").upper().strip()

        if action == "START":
            request.session.pop(TUTORIAL_SESSION_KEY, None)
            return redirect("blackjack_lobby")

        if action == engine_api.ACTION_NEW:
            engine.start_betting_round()

        elif action == engine_api.ACTION_CONFIRM_BET:
            if engine.phase == Phase.BETTING:
                raw_bet = request.POST.get("bet_amount", str(GameEngine.DEFAULT_MIN_BET))
                try:
                    bet = int(raw_bet)
                except (TypeError, ValueError):
                    bet = GameEngine.DEFAULT_MIN_BET

                engine.player_bets[0][0] = bet
                engine.confirm_bet(0)
            else:
                engine.message = "Bet confirmation is only allowed during betting."

        elif action == engine_api.ACTION_DEAL:
            bets = [seat_bets[0] for seat_bets in engine.player_bets]
            engine.complete_betting_and_deal(bets)

        # [M5] tutorial insurance
        elif action == engine_api.ACTION_TAKE_INSURANCE:
            engine.decide_insurance(0, True)

        elif action == engine_api.ACTION_SKIP_INSURANCE:
            engine.decide_insurance(0, False)

        elif action in {
            engine_api.ACTION_HIT,
            engine_api.ACTION_STAND,
            engine_api.ACTION_DOUBLE,
            engine_api.ACTION_SPLIT,
            engine_api.ACTION_SURRENDER,
        }:
            engine_api.apply_action(engine, action)

        _save_tutorial_engine(request, engine)
        return redirect("blackjack_tutorial")

    state = engine_api.get_view_state_for_player(engine, 0, "TUTORIAL")
    state["is_host"] = True
    state["participant_count"] = 1
    state["max_players"] = 1
    state["is_tutorial_room"] = True
    return render(request, "UI.html", {"mode": "room", "state": state})

def _ensure_session(request: HttpRequest) -> str:
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def _generate_code(length: int = 6) -> str:
    chars = string.ascii_uppercase + string.digits
    while True:
        code = "".join(random.choice(chars) for _ in range(length))
        if not GameTable.objects.filter(code=code).exists():
            return code


def _load_engine(table: GameTable) -> GameEngine:
    engine = engine_api.import_state(table.engine_state)
    if engine is None:
        engine = GameEngine(num_players=table.max_players)
        table.engine_state = engine_api.export_state(engine)
        table.status = engine.phase.name
        table.save(update_fields=["engine_state", "status", "updated_at"])
    return engine


def _save_engine(table: GameTable, engine: GameEngine) -> None:
    table.engine_state = engine_api.export_state(engine)
    table.status = engine.phase.name
    table.save(update_fields=["engine_state", "status", "updated_at"])


def _viewer_participant(request: HttpRequest, table: GameTable) -> TableParticipant:
    session_key = _ensure_session(request)
    participant = table.participants.filter(session_key=session_key).first()
    if participant is None:
        raise Http404("You are not part of this table.")
    return participant


@require_http_methods(["GET", "POST"])
def lobby(request: HttpRequest) -> HttpResponse:
    session_key = _ensure_session(request)

    if request.method == "POST":
        action = (request.POST.get("action") or "").upper().strip()

        if action == "CREATE":
            try:
                max_players = int(request.POST.get("num_players", 2))
            except (TypeError, ValueError):
                max_players = 2
            max_players = max(2, min(4, max_players))
            name = (request.POST.get("player_name") or "Host").strip()[:32] or "Host"

            with transaction.atomic():
                table = GameTable.objects.create(
                    code=_generate_code(),
                    host_session_key=session_key,
                    max_players=max_players,
                    status=Phase.WAITING.name,
                    engine_state={},
                )
                engine = GameEngine(num_players=max_players)
                engine.set_player_name(0, name)
                engine.set_player_ready(0, True)
                _save_engine(table, engine)

                TableParticipant.objects.create(
                    table=table,
                    seat_index=0,
                    name=name,
                    session_key=session_key,
                    is_host=True,
                    is_ready=True,
                )

            return redirect("blackjack_room", code=table.code)

        if action == "JOIN":
            code = (request.POST.get("table_code") or "").strip().upper()
            name = (request.POST.get("player_name") or "Player").strip()[:32] or "Player"
            table = get_object_or_404(GameTable, code=code)

            with transaction.atomic():
                existing = table.participants.filter(session_key=session_key).first()
                if existing is None:
                    used_seats = set(table.participants.values_list("seat_index", flat=True))
                    seat_index = None
                    for idx in range(table.max_players):
                        if idx not in used_seats:
                            seat_index = idx
                            break
                    if seat_index is None:
                        return render(
                            request,
                            "UI.html",
                            {
                                "mode": "lobby",
                                "error": "This table is already full.",
                            },
                        )
                    participant = TableParticipant.objects.create(
                        table=table,
                        seat_index=seat_index,
                        name=name,
                        session_key=session_key,
                        is_host=False,
                        is_ready=True,
                    )
                else:
                    participant = existing
                    participant.name = name
                    participant.is_ready = True
                    participant.save(update_fields=["name", "is_ready"])

                engine = _load_engine(table)
                engine.set_player_name(participant.seat_index, participant.name)
                engine.set_player_ready(participant.seat_index, True)
                _save_engine(table, engine)

            return redirect("blackjack_room", code=table.code)

    my_tables = GameTable.objects.filter(participants__session_key=session_key).distinct().order_by("-updated_at")[:5]
    return render(request, "UI.html", {"mode": "lobby", "my_tables": my_tables})

@require_http_methods(["GET", "POST"])
def room(request: HttpRequest, code: str) -> HttpResponse:
    table = get_object_or_404(GameTable, code=code.upper())
    participant = _viewer_participant(request, table)

    with transaction.atomic():
        engine = _load_engine(table)

        if request.method == "POST":
            action = (request.POST.get("action") or "").upper().strip()

            if action == "LEAVE":
                participant.delete()
                return redirect("blackjack_lobby")

            if action == "READY":
                participant.is_ready = True
                participant.save(update_fields=["is_ready"])
                engine.set_player_ready(participant.seat_index, True)

            elif action == engine_api.ACTION_NEW:
                if participant.is_host:
                    engine.start_betting_round()
                else:
                    engine.message = "Only the host can open the next round setup."

            elif action == engine_api.ACTION_CONFIRM_BET:
                if engine.phase == Phase.BETTING:
                    raw_bet = request.POST.get("bet_amount", str(GameEngine.DEFAULT_MIN_BET))
                    try:
                        bet = int(raw_bet)
                    except (TypeError, ValueError):
                        bet = GameEngine.DEFAULT_MIN_BET

                    engine.player_bets[participant.seat_index][0] = bet
                    engine.confirm_bet(participant.seat_index)
                else:
                    engine.message = "Bet confirmation is only allowed during betting."

            elif action == engine_api.ACTION_DEAL:
                if participant.is_host:
                    bets = [seat_bets[0] for seat_bets in engine.player_bets]
                    engine.complete_betting_and_deal(bets)
                else:
                    engine.message = "Only the host can deal cards."

            elif action == engine_api.ACTION_TAKE_INSURANCE:
                engine.decide_insurance(participant.seat_index, True)

            elif action == engine_api.ACTION_SKIP_INSURANCE:
                engine.decide_insurance(participant.seat_index, False)

            elif action in {
                engine_api.ACTION_HIT,
                engine_api.ACTION_STAND,
                engine_api.ACTION_DOUBLE,
                engine_api.ACTION_SPLIT,
                engine_api.ACTION_SURRENDER,
            }:
                if participant.seat_index != engine.current_player_index:
                    engine.message = "It is not your turn."
                else:
                    engine_api.apply_action(engine, action)

            _save_engine(table, engine)
            return redirect("blackjack_room", code=table.code)

    state = engine_api.get_view_state_for_player(engine, participant.seat_index, table.code)
    state["is_host"] = participant.is_host
    state["participant_count"] = table.participants.count()
    state["max_players"] = table.max_players
    return render(request, "UI.html", {"mode": "room", "state": state})

# ----------------------------
# AJAX endpoints for partial refresh
# ----------------------------

@require_http_methods(["GET"])
def room_state(request: HttpRequest, code: str) -> JsonResponse:
    table = get_object_or_404(GameTable, code=code.upper())
    participant = _viewer_participant(request, table)
    engine = _load_engine(table)

    state = engine_api.get_view_state_for_player(
        engine,
        participant.seat_index,
        table.code,
    )
    state["is_host"] = participant.is_host
    state["participant_count"] = table.participants.count()
    state["max_players"] = table.max_players

    return JsonResponse(state)


@require_http_methods(["POST"])
def room_action_json(request: HttpRequest, code: str) -> JsonResponse:
    table = get_object_or_404(GameTable, code=code.upper())
    participant = _viewer_participant(request, table)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    action = (payload.get("action") or "").upper().strip()

    with transaction.atomic():
        engine = _load_engine(table)

        # M5: NEW round setup must also work through AJAX
        if action == engine_api.ACTION_NEW:
            if participant.is_host:
                engine.start_betting_round()
            else:
                engine.message = "Only the host can open the next round setup."

        # M5: insurance is seat-based, not current-turn based
        elif action == engine_api.ACTION_TAKE_INSURANCE:
            engine.decide_insurance(participant.seat_index, True)

        elif action == engine_api.ACTION_SKIP_INSURANCE:
            engine.decide_insurance(participant.seat_index, False)

        elif action == engine_api.ACTION_CONFIRM_BET:
            if engine.phase == Phase.BETTING:
                raw_bet = payload.get("bet_amount", GameEngine.DEFAULT_MIN_BET)
                try:
                    bet = int(raw_bet)
                except (TypeError, ValueError):
                    bet = GameEngine.DEFAULT_MIN_BET

                engine.player_bets[participant.seat_index][0] = bet
                engine.confirm_bet(participant.seat_index)
            else:
                engine.message = "Bet confirmation is only allowed during betting."

        elif action == engine_api.ACTION_DEAL:
            if participant.is_host:
                bets = [seat_bets[0] for seat_bets in engine.player_bets]
                engine.complete_betting_and_deal(bets)
            else:
                engine.message = "Only the host can deal cards."

        elif action in {
            engine_api.ACTION_HIT,
            engine_api.ACTION_STAND,
            engine_api.ACTION_DOUBLE,
            engine_api.ACTION_SPLIT,
            engine_api.ACTION_SURRENDER,
        }:
            if participant.seat_index != engine.current_player_index:
                engine.message = "It is not your turn."
            else:
                engine_api.apply_action(engine, action)

        else:
            engine.message = f"Unknown action: {action}"

        _save_engine(table, engine)

    state = engine_api.get_view_state_for_player(
        engine,
        participant.seat_index,
        table.code,
    )
    state["is_host"] = participant.is_host
    state["participant_count"] = table.participants.count()
    state["max_players"] = table.max_players

    return JsonResponse(state)