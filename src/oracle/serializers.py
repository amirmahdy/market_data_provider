from rest_framework import serializers


class DateSerializer(serializers.Serializer):
    date = serializers.DateField(required=False, input_formats=["%Y%m%d", "%Y-%m-%d"])


class InstrumentSerializer(serializers.Serializer):
    isin = serializers.RegexField(regex=r'^(IR\w{10},*)*$', required=True)


class InstrumentDateSerializer(serializers.Serializer):
    isin = serializers.RegexField(regex=r'^(IR\w{10},*)*$', required=True)
    date = serializers.DateField(required=False, input_formats=["%Y%m%d", "%Y-%m-%d"])
