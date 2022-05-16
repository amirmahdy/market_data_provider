from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from oracle.serializers import InstrumentDateSerializer
from oracle.data_type.instrument_market_data import InstrumentData
from rest_framework import status
from drf_yasg import openapi
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from mdp.utils import read_csv
from mdp import settings
from oracle.models import Instrument
from datetime import datetime

isin_param = openapi.Parameter('isin', openapi.IN_QUERY, description="ISIN Param", type=openapi.TYPE_STRING)
date_param = openapi.Parameter('date', openapi.IN_QUERY, description="Date Param", type=openapi.TYPE_STRING)


class TradeDataAPIView(GenericAPIView):
    serializer_class = InstrumentDateSerializer

    @swagger_auto_schema(methods=["get"], manual_parameters=[isin_param, date_param])
    @action(detail=False, methods=["get"])
    def get(self, request, *args, **kwargs):
        """
        input   -- ISIN
        input   -- Date
        output  -- Trades History
        """
        serializer = self.serializer_class(data=request.GET)
        if serializer.is_valid():
            data = serializer.validated_data
            if data.get("date") is None:
                res = InstrumentData.get(isin=data["isin"], ref_group="trades")

            else:
                instrument = Instrument.get_instrument(data["isin"])[0]
                date = datetime.strftime(data["date"], "%Y%m%d")

                path = settings.DATA_ROOT + "/trade/" + instrument.en_symbol.lower() + "/" + date + ".csv"
                res = read_csv(path)

            return Response({"message": res}, status=status.HTTP_200_OK)

        else:
            return Response({"message": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
