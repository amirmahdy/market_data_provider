from django.contrib import admin
from .models import Instrument, InstrumentType, TriggerParameter

admin.site.register(Instrument)
admin.site.register(InstrumentType)
admin.site.register(TriggerParameter)