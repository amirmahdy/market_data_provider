from django.contrib import admin
from .models import Instrument, InstrumentType, TriggerParameter, Sources


@admin.register(TriggerParameter)
class TriggerParameterAdmin(admin.ModelAdmin):
    readonly_fields = ('name', 'name_fa', 'description', 'trigger_name')


admin.site.register(Instrument)
admin.site.register(Sources)
admin.site.register(InstrumentType)
