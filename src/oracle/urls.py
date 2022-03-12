from django.urls import path
from .views.test import CaptchaAPIView
from .views.instrument import InstrumentAppendAPIView

urlpatterns = [
    path("tsetmc", CaptchaAPIView.as_view(), name="test"),
    path("instrument_append", InstrumentAppendAPIView.as_view(), name="instruments-append"),
]
