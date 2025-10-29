# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Player, Match, MatchData
import json

@csrf_exempt
def find_match(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body.decode())
    player_id = data.get("player_id")
    if not player_id:
        return JsonResponse({"error": "player_id required"}, status=400)

    player, _ = Player.objects.get_or_create(player_id=player_id)

    # Already matched
    if player.current_match and not player.waiting:
        opponent = Player.objects.exclude(player_id=player_id).filter(current_match=player.current_match).first()
        return JsonResponse({
            "status": "matched",
            "opponent_id": opponent.player_id,
            "job": player.job,
            "match_id": str(player.current_match.match_id)
        })

    # Try to find opponent
    waiting_opponent = Player.objects.filter(waiting=True).exclude(player_id=player_id).first()
    if waiting_opponent:
        # Create new match
        match = Match.objects.create()
        # Update both players
        player.current_match = match
        player.job = "client"
        player.waiting = False
        player.save()

        waiting_opponent.current_match = match
        waiting_opponent.job = "host"
        waiting_opponent.waiting = False
        waiting_opponent.save()

        return JsonResponse({
            "status": "matched",
            "opponent_id": waiting_opponent.player_id,
            "job": "client",
            "match_id": str(match.match_id)
        })

    # No opponent → wait
    player.waiting = True
    player.current_match = None
    player.save()
    return JsonResponse({"status": "waiting"})


@csrf_exempt
def send_match_data(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body.decode())
    player_id = data.get("player_id")
    match_id = data.get("match_id")
    payload = data.get("payload")

    if not player_id or not match_id or payload is None:
        return JsonResponse({"error": "player_id, match_id, and payload required"}, status=400)

    try:
        match = Match.objects.get(match_id=match_id)
        player = Player.objects.get(player_id=player_id)
    except (Match.DoesNotExist, Player.DoesNotExist):
        return JsonResponse({"error": "invalid match_id or player_id"}, status=400)

    MatchData.objects.update_or_create(
        match=match,
        player=player,
        defaults={"payload": payload}
    )
    return JsonResponse({"status": "ok"})


@csrf_exempt
def fetch_opponent_data(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body.decode())
    player_id = data.get("player_id")
    match_id = data.get("match_id")

    if not player_id or not match_id:
        return JsonResponse({"error": "player_id and match_id required", "opponent_data": None}, status=400)

    try:
        player = Player.objects.get(player_id=player_id)
        match = player.current_match
        if not match:
            return JsonResponse({"status": "ok", "opponent_data": None})
        opponent = Player.objects.exclude(player_id=player_id).filter(current_match=match).first()
        if not opponent:
            return JsonResponse({"status": "ok", "opponent_data": None})
        opponent_data = MatchData.objects.filter(match=match, player=opponent).first()
        return JsonResponse({"status": "ok", "opponent_data": opponent_data.payload if opponent_data else None})
    except Player.DoesNotExist:
        return JsonResponse({"status": "ok", "opponent_data": None})
