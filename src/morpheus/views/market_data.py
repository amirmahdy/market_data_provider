from rest_framework.response import Response
from rest_framework.generics import GenericAPIView


class MarketDataAPIView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "Done"})
