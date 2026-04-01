from django.urls import path
from . import views

urlpatterns = [
    path("", views.lobby, name="blackjack_lobby"),
    path("table/<str:code>/", views.room, name="blackjack_room"),
    path("tutorial/", views.tutorial, name="blackjack_tutorial"),
]