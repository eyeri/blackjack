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
    path("", views.index, name="index"),
]
