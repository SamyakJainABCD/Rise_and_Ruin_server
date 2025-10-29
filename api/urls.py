from django.urls import path
from .views import find_match, send_match_data, fetch_opponent_data

urlpatterns = [
    path("find_match/", find_match),
    path("send_match_data/", send_match_data),
    path("fetch_opponent_data/", fetch_opponent_data),
]