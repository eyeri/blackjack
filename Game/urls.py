from django.urls import path
from . import views

urlpatterns = [
    path("", views.lobby, name="blackjack_lobby"),
    path("table/<str:code>/", views.room, name="blackjack_room"),
    path("table/<str:code>/state/", views.room_state, name="blackjack_room_state"),
    path("table/<str:code>/action/", views.room_action_json, name="blackjack_room_action"),
    path("tutorial/", views.tutorial, name="blackjack_tutorial"),
]