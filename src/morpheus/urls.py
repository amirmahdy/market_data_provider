from django.urls import path
from morpheus.views.market_data import MarketDataAPIView
from morpheus.views.trades_history import TradeDataAPIView

urlpatterns = [
    path("market_data", MarketDataAPIView.as_view(), name="market-data"),
    path('trade_data', TradeDataAPIView.as_view(), name='trade-data')
]
