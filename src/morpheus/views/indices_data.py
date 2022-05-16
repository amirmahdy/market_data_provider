from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.decorators import action
from oracle.serializers import InstrumentSerializer
from oracle.services.tsetmc_indices import get_indices_live


class IndicesDataAPIView(GenericAPIView):
    serializer_class = InstrumentSerializer

    @action(detail=False, methods=['get'])
    def get(self, request, *args, **kwargs):
        try:
            res = get_indices_live()
            return Response({"message": res}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": repr(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
