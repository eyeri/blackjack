# views.py
"""
View placeholder.

This file will handle UI requests and delegate
game logic processing to engine_api.py.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from .engine import GameEngine
from .engine_api import get_view_state

def index(request):
    """
    Placeholder view.

    UI team will implement request handling logic here.
    """
    # TODO (Milestone 3):
    # - Add user-facing messages and explanations for learning support
    # - Improve UI presentation (layout, styling)

    return render(request, 'blackjack/index.html')

def milestone2_api_demo(request):
    """
    PROTOTYPE VALIDATION ONLY:
    This view proves that the core engine and the API contract (engine_api.py)
    are functional within the Django framework. 
    Full session management and UI integration are deferred to Milestone 3.
    """
    # Initialize the robust engine
    engine = GameEngine()
    engine.new_round() # Executes initial deal
    
    # Generate the View State (JSON)
    # This proves we can communicate game state to a front-end
    view_data = get_view_state(engine, hide_dealer_hole=True)
    
    return JsonResponse({
        "milestone": 2,
        "validation_status": "Passed",
        "logic_verification": "Engine-to-API bridge functional",
        "game_data": view_data
    })