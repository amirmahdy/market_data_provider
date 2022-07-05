from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.decorators import action
from oracle.data_type.heart_beat import HeartBeat


class HeartBeatDataAPIView(GenericAPIView):

    @action(detail=False, methods=['get'])
    def get(self, request, *args, **kwargs):
        try:
            source = "O+"
            value_list = ["index", "askbid", "market", "state", "indinst"]
            res = []
            for value in value_list:
                new_dict = {
                    "ref_group": source,
                    "ref_value": value
                }
                item = HeartBeat.get(source, value)
                if item:
                    new_dict.update(item)
                    res.append(new_dict)

            return Response({"message": res}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": repr(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)