import os, django
from django.test import TestCase


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mdp.settings")
django.setup()


class Test_Service(TestCase):

    def test_askbid(self):
        from oracle.data_type.instrument_market_data import InstrumentData
        from oracle.services.tsetmc_trades import get_trades
        res = get_trades('48010225447410247', '20220101')
        InstrumentData.update("IRO1BANK0001", "trades", res)
        print(res)


tr = Test_Service()
tr.test_askbid()
