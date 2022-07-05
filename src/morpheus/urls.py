from django.urls import path

from morpheus.views.heart_beat_data import HeartBeatDataAPIView
from morpheus.views.market_data import MarketDataAPIView
from morpheus.views.trades_history import TradeDataAPIView
from morpheus.views.askbid_data import AskBidDataAPIView, FullAskBidDataAPIView
from morpheus.views.indices_data import IndicesDataAPIView
from morpheus.views.indinst_data import IndInstDataAPIView
from morpheus.views.state_data import StateDataAPIView

urlpatterns = [
    path("market", MarketDataAPIView.as_view(), name="market"),
    path("state", StateDataAPIView.as_view(), name="state"),
    path("askbid", AskBidDataAPIView.as_view(), name="askbid"),
    path("indices", IndicesDataAPIView.as_view(), name="index"),
    path("indinst", IndInstDataAPIView.as_view(), name="indinst"),
    path("full_askbid", FullAskBidDataAPIView.as_view(), name="full_askbid"),
    path('trade', TradeDataAPIView.as_view(), name='trade'),
    path('heart_beat', HeartBeatDataAPIView.as_view(), name='heart_beat')
]
