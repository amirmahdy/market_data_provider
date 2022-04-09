from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from oracle.serializers import InstrumentSerializer
from oracle.data_type.instrument_market_data import InstrumentData
from rest_framework import status


class TradesHistoryAPIView(GenericAPIView):

    serializer_class = InstrumentSerializer

    def get(self, request, *args, **kwargs):
        """
        input   -- ISIN
        output  -- Trades History
        """
        serializer = InstrumentSerializer(data=request.GET)
        if serializer.is_valid():
            data = serializer.validated_data
            res = InstrumentData.get(
                isin=data['isin'], ref_group='today_trades')
            return Response({"message": res}, status=status.HTTP_200_OK)
        else:
            return Response({"message": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
