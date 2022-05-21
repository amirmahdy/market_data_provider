from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from drf_yasg import openapi
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from oracle.serializers import InstrumentDateSerializer, InstrumentSerializer
from oracle.data_type.instrument_market_data import InstrumentData
from mdp import settings
from oracle.models import Instrument
from datetime import datetime
from mdp.utils import read_csv

isin_param = openapi.Parameter('isin', openapi.IN_QUERY, description="ISIN Param", type=openapi.TYPE_STRING)
date_param = openapi.Parameter('date', openapi.IN_QUERY, description="Date Param", type=openapi.TYPE_STRING)


class AskBidDataAPIView(GenericAPIView):
    serializer_class = InstrumentDateSerializer

    @swagger_auto_schema(methods=['get'], manual_parameters=[isin_param, date_param])
    @action(detail=False, methods=['get'])
    def get(self, request, *args, **kwargs):
        """
        input   -- ISIN
        output  -- Market Data
        """
        serializer = InstrumentDateSerializer(data=request.GET)
        if serializer.is_valid():
            data = serializer.validated_data
            if data.get("date") is None:
                res = InstrumentData.get(isin=data['isin'], ref_group='askbid')
            else:
                instrument = Instrument.get_instrument(data["isin"])[0]
                date = datetime.strftime(data["date"], "%Y%m%d")
                path = settings.DATA_ROOT + "/askbid/" + instrument.en_symbol.lower() + "/" + date + ".csv"
                res = read_csv(path, fieldnames=["time", "buy_price_1", "buy_volume_1", "buy_count_1", "sell_price_1",
                                                 "sell_volume_1", "sell_count_1", "buy_price_2", "buy_volume_2",
                                                 "buy_count_2", "sell_price_2", "sell_volume_2", "sell_count_2",
                                                 "buy_price_3", "buy_volume_3", "buy_count_3", "sell_price_3",
                                                 "sell_volume_3", "sell_count_3", "buy_price_4", "buy_volume_4",
                                                 "buy_count_4", "sell_price_4", "sell_volume_4", "sell_count_4",
                                                 "buy_price_5", "buy_volume_5", "buy_count_5", "sell_price_5",
                                                 "sell_volume_5", "sell_count_5"])
            return Response({"message": res}, status=status.HTTP_200_OK)
        else:
            return Response({"message": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)


class FullAskBidDataAPIView(GenericAPIView):
    serializer_class = InstrumentSerializer

    @swagger_auto_schema(methods=['get'], manual_parameters=[isin_param])
    @action(detail=False, methods=['get'])
    def get(self, request, *args, **kwargs):
        """
        input   -- ISIN
        output  -- Market Data
        """
        serializer = InstrumentSerializer(data=request.GET)
        if serializer.is_valid():
            data = serializer.validated_data
            res = InstrumentData.get(isin=data['isin'], ref_group='full_askbid')
            return Response({"message": res}, status=status.HTTP_200_OK)
        else:
            return Response({"message": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
