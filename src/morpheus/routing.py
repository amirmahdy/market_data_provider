from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/fee/', consumers.DashboardConsumer.as_asgi()),
]