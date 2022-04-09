from django.urls import path
from morpheus.views.market_data import MarketDataAPIView
from morpheus.views.trades_history import TradesHistoryAPIView

urlpatterns = [
    path("market_data", MarketDataAPIView.as_view(), name="market-data"),
    path('trades_history', TradesHistoryAPIView.as_view(), name='trades-history')
]
