from django.contrib import admin
from .models import Instrument, InstrumentType

admin.site.register(Instrument)
admin.site.register(InstrumentType)
