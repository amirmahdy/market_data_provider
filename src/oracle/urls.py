from django.urls import path
from .views.instrument import InstrumentAppendAPIView

urlpatterns = [
    path("instrument_append", InstrumentAppendAPIView.as_view(), name="instruments-append"),
]
