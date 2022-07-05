from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from oracle.models import Instrument, InstrumentType
import requests
import xmltodict
import ast
import csv
from threading import Thread
import environ
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from oracle.serializers import InstrumentSerializer

env = environ.Env()


class InstrumentAppendAPIView(GenericAPIView):
    serializer_class = InstrumentSerializer

    @swagger_auto_schema(methods=['post'], request_body=InstrumentSerializer)
    @action(detail=False, methods=['post'])
    def post(self, request, *args, **kwargs):
        """
        A method for updating instrument DB
        """
        serializer = InstrumentSerializer(data=request.data)
        if serializer.is_valid():
            cisins = serializer.validated_data['isin']
            if cisins is not None:
                t = Thread(target=self.background_instrument_fetch, args=(cisins.split(','),))
                t.start()
            else:
                with open("oracle/fixtures/instrument.csv", "rt") as fp:
                    cisins_csv = csv.reader(fp, delimiter=',')
                    cisins = [cisin_csv[0] for cisin_csv in cisins_csv]

                t = Thread(target=self.background_instrument_fetch, args=(cisins,))
                t.start()
            return Response({"Response": "Process is undergoing"})
        else:
            return Response({"Response": "Wrong ISIN data"})

    def get_tadbir_id(self, symbol, current_val):
        if current_val == '' or current_val is None:
            url = f"https://api.bmibourse.ir/Web/V1/Symbol/GetSymbol?term={symbol}"
            response = requests.get(url)
            response = ast.literal_eval(response.text)
            return response[0]['value']
        else:
            return current_val.tadbir_id

    def background_instrument_fetch(self, cisins):
        """
        Generates a complete list of instruments
        """
        url = "http://service.tsetmc.com/WebService/TsePublicV2.asmx?op=Instrument"
        headers = {
            "content-type": "text/xml",
            "SOAPAction": "http://tsetmc.com/Instrument",
        }
        body = """<?xml version="1.0" encoding="utf-8"?>
                                    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                                      <soap:Body>
                                        <Instrument xmlns="http://tsetmc.com/">
                                          <UserName>{0}</UserName>
                                          <Password>{1}</Password>
                                          <Flow>0</Flow>
                                        </Instrument>
                                      </soap:Body>
                                    </soap:Envelope>""".format(
            env("TSETMC_USERNAME"), env("TSETMC_PASSWORD")
        )

        response = requests.post(url, data=body, headers=headers)
        xml_raw = response.content.decode("utf-8")
        xml_data = xmltodict.parse(xml_raw)
        xml_data = xml_data['soap:Envelope']['soap:Body']['InstrumentResponse']['InstrumentResult'] \
            ['diffgr:diffgram']['Instruments']['TseInstruments']

        instruments = []
        current_instruments = Instrument.objects.select_related().all()
        current_instruments = {x.isin: x for x in current_instruments}
        for data in xml_data:
            if data["InstrumentID"] in cisins:
                instruments.append(
                    Instrument(
                        last_trade_date=int(data["DEVen"]),
                        tse_id=data["InsCode"],
                        isin=data["InstrumentID"],
                        en_symbol=data["CValMne"],
                        en_symbol_18=data["LVal18"],
                        en_code_5=data["CSocCSAC"],
                        name=data["LSoc30"],
                        symbol=data["LVal18AFC"],
                        fa_symbol_30=data["LSoc30"],
                        cisin=data["CIsin"],
                        nominal_val=data["QNmVlo"],
                        stock_qnt=float(data["ZTitad"]),
                        change_date=int(data["DESop"]),
                        change_type=int(data["YOPSJ"]),
                        shit_type_AIO=data["CGdSVal"],
                        group_code=data["CGrValCot"],
                        initial_date=int(data["DInMar"]),
                        unit=int(data["YUniExpP"]),
                        market_code=data["YMarNSC"],
                        board_code=data["CComVal"],
                        ind_code=data["CSecVal"],
                        sub_ind_code=data["CSoSecVal"],
                        clear_delay=int(data["YDeComp"]),
                        max_allowed_price=float(data["PSaiSMaxOkValMdv"]),
                        min_allowed_price=float(data["PSaiSMinOkValMdv"]),
                        base_vol=int(data["BaseVol"]),
                        type=InstrumentType.objects.get(
                            pk=int(data["YVal"])
                        ),
                        tick_size=int(float(data["QPasCotFxeVal"])),
                        trans_min_size=int(data["QQtTranMarVal"]),
                        flow=int(data["Flow"]),
                        valid=int(data["Valid"]),
                        order_min_size=int(data["QtitMinSaiOmProd"]),
                        order_max_size=int(data["QtitMaxSaiOmProd"]),
                        market_status="A",
                        tadbir_id=self.get_tadbir_id(data["CValMne"], current_instruments.get(data['InstrumentID']))
                    )
                )

        Instrument.objects.bulk_create(instruments, ignore_conflicts=True)
        Instrument.objects.bulk_update(
            instruments,
            fields=[
                "last_trade_date",
                "tse_id",
                "en_symbol",
                "en_symbol_18",
                "en_code_5",
                "name",
                "symbol",
                "fa_symbol_30",
                "cisin",
                "nominal_val",
                "stock_qnt",
                "change_date",
                "change_type",
                "shit_type_AIO",
                "group_code",
                "initial_date",
                "unit",
                "market_code",
                "board_code",
                "ind_code",
                "sub_ind_code",
                "clear_delay",
                "max_allowed_price",
                "min_allowed_price",
                "base_vol",
                "type",
                "tick_size",
                "trans_min_size",
                "flow",
                "valid",
                "order_min_size",
                "order_max_size",
                "market_status",
                "tadbir_id"
            ],
            batch_size=1000,
        )
