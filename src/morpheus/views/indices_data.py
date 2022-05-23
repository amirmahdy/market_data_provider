from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.decorators import action
from oracle.serializers import InstrumentSerializer
from oracle.services.tsetmc_indices import get_indices_live
from oracle.data_type.instrument_market_data import InstrumentData


class IndicesDataAPIView(GenericAPIView):
    serializer_class = InstrumentSerializer

    @action(detail=False, methods=['get'])
    def get(self, request, *args, **kwargs):
        try:
            indices = ["IRX6XS300006", "IRX6XSNT0006", "IRXYXTPI0026", "IRX6XTPI0006", "IRX6XSLC0006"]
            res = []
            for index in indices:
                res.append(InstrumentData.get(index, 'index'))

            return Response({"message": res}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": repr(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
