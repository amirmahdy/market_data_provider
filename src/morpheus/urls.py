from django.urls import path
from morpheus.views.market_data import MarketDataAPIView

urlpatterns = [
    path("market_data", MarketDataAPIView.as_view(), name="market-data"),
]
