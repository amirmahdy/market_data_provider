from rest_framework import serializers


class InstrumentSerializer(serializers.Serializer):
    isin = serializers.CharField(max_length=200)
