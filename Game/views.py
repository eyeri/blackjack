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
from django.shortcuts import render

def index(request):
    """
    Placeholder view.

    UI team will implement request handling logic here.
    """
    # TODO (Milestone 3):
    # - Add user-facing messages and explanations for learning support
    # - Improve UI presentation (layout, styling)

    return render(request, 'blackjack/index.html')

def main_page(request):
    return render(request, 'UI.html')