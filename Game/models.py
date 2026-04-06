from django.db import models


class GameTable(models.Model):
    STATUS_WAITING = "WAITING"
    STATUS_BETTING = "BETTING"
    STATUS_PLAYER_TURN = "PLAYER_TURN"
    STATUS_DEALER_TURN = "DEALER_TURN"
    STATUS_ROUND_OVER = "ROUND_OVER"

    STATUS_CHOICES = [
        (STATUS_WAITING, "Waiting"),
        (STATUS_BETTING, "Betting"),
        (STATUS_PLAYER_TURN, "Player Turn"),
        (STATUS_DEALER_TURN, "Dealer Turn"),
        (STATUS_ROUND_OVER, "Round Over"),
    ]

    code = models.CharField(max_length=8, unique=True)
    host_session_key = models.CharField(max_length=64, blank=True)
    max_players = models.PositiveSmallIntegerField(default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_WAITING)
    engine_state = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Table {self.code} ({self.status})"


class TableParticipant(models.Model):
    table = models.ForeignKey(GameTable, on_delete=models.CASCADE, related_name="participants")
    seat_index = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=32, default="Player")
    session_key = models.CharField(max_length=64)
    is_host = models.BooleanField(default=False)
    is_ready = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("table", "seat_index"), ("table", "session_key")]
        ordering = ["seat_index"]

    def __str__(self) -> str:
        return f"{self.table.code} / seat {self.seat_index + 1} / {self.name}"
