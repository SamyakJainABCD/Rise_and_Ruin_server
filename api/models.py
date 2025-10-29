# models.py
from django.db import models
import uuid

class Match(models.Model):
    match_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Player(models.Model):
    player_id = models.CharField(max_length=100, unique=True)
    # Track current match if any
    current_match = models.ForeignKey(Match, null=True, blank=True, on_delete=models.SET_NULL)
    job = models.CharField(max_length=10, null=True, blank=True)  # "host" or "client"
    waiting = models.BooleanField(default=True)

class MatchData(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="match_data")
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
