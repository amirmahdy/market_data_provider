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

    def test_get_kline(self):
        from oracle.services.tsetmc_trades import get_kline
        import environ
        from oracle.models import Instrument

        env = environ.Env()
        instruments = Instrument.get_instruments()

        res = get_kline("20220101", "20220103", instruments[0].tse_id, env("TSETMC_USERNAME"), env("TSETMC_PASSWORD"))
        print(res)

    def test_task_kline(self):
        from oracle.tasks import trade_data_yesterday_update
        res = trade_data_yesterday_update()
        print(res)


tr = Test_Service()
tr.test_task_kline()
