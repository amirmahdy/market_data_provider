from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from drf_yasg import openapi
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from oracle.serializers import InstrumentSerializer
from oracle.data_type.instrument_market_data import InstrumentData

isin_param = openapi.Parameter('isin', openapi.IN_QUERY, description="ISIN Param", type=openapi.TYPE_STRING)


class StateDataAPIView(GenericAPIView):
    serializer_class = InstrumentSerializer

    @swagger_auto_schema(methods=['get'], manual_parameters=[isin_param])
    @action(detail=False, methods=['get'])
    def get(self, request, *args, **kwargs):
        """
        input   -- ISIN
        output  -- state Data
        """
        serializer = InstrumentSerializer(data=request.GET)
        if serializer.is_valid():
            data = serializer.validated_data
            res = InstrumentData.get(isin=data['isin'], ref_group='state')
            return Response({"message": res}, status=status.HTTP_200_OK)
        else:
            return Response({"message": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
