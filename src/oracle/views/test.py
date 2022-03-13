from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from oracle.services.tsetmc_market_data import get_tse_instrument_data


class CaptchaSerializer(serializers.Serializer):
    email = serializers.EmailField()
    content = serializers.CharField(max_length=200)
    created = serializers.DateTimeField()


class CaptchaAPIView(APIView):
    serializer_class = CaptchaSerializer

    def get(self, request, *args, **kwargs):
        """
        Call for TSETMC service
        """
        # data = get_tse_instrument_data("8725363201030474")
        return Response({"res": 0})
