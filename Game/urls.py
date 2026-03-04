# urls.py
"""
URL routing placeholder.

This file will define routes that connect
UI requests to view functions.
"""

from django.contrib import admin
from django.urls import path
from Game import views

urlpatterns = [
    # Placeholder route
    path('admin/', admin.site.get_urls() if hasattr(admin.site, 'get_urls') else admin.site.urls),
    # TODO (Milestone 3):
    # - Add URL routes for advanced actions (DOUBLE, SPLIT)
    # - Introduce route-level validation once full rule set is implemented
    path('milestone2_api_demo/', views.milestone2_api_demo, name='api_demo'),
]
