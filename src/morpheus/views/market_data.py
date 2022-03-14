from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from drf_yasg import openapi
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from oracle.data_type.instrument_market_data import Instrument_Maker_Data

isin_param = openapi.Parameter('isin', openapi.IN_QUERY, description="ISIN Param", type=openapi.TYPE_STRING)


class InstrumentSerializer(serializers.Serializer):
    isin = serializers.CharField(max_length=200)


class MarketDataAPIView(GenericAPIView):

    @swagger_auto_schema(methods=['get'], manual_parameters=[isin_param])
    @action(detail=False, methods=['get'])
    def get(self, request, *args, **kwargs):
        """
        input   -- ISIN
        output  -- Market Data
        """
        serializer_class = InstrumentSerializer(data=request.GET)
        if serializer_class.is_valid():
            data = serializer_class.validated_data
            res = Instrument_Maker_Data.get(isin=data['isin'])
            return Response({"message": res}, status=status.HTTP_200_OK)
        else:
            return Response({"message": str(serializer_class.errors)}, status=status.HTTP_400_BAD_REQUEST)
