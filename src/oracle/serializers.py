from rest_framework import serializers


class InstrumentSerializer(serializers.Serializer):
    isin = serializers.RegexField(regex=r'^(IR\w\d\w{4}\d{4})$', required=True)
    date = serializers.DateField(required=False, input_formats=["%Y%m%d", "%Y-%m-%d"])
