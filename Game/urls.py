# urls.py
"""
URL routing placeholder.

This file will define routes that connect
UI requests to view functions.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Placeholder route
    
    # TODO (Milestone 3):
    # - Add URL routes for advanced actions (DOUBLE, SPLIT)
    # - Introduce route-level validation once full rule set is implemented

    path("", views.index, name="index"),
]
