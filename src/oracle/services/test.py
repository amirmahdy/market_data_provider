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

    def test_get_live_askbid(self):
        from oracle.models import Instrument
        from oracle.services.tsetmc_askbid import get_live_askbid
        instruments = Instrument.get_instrument("IRO1BANK0001")

        res = get_live_askbid(instruments[0].tse_id)
        print(res)


    def test_get_tse_instrument_data(self):
        from oracle.models import Instrument
        from oracle.services.tsetmc_market import get_tse_instrument_data
        instruments = Instrument.get_instrument("IRO1BANK0001")
        get_tse_instrument_data(instruments[0].tse_id)

    def test_get_index(self):
        from pytse_client.download import download_financial_indexes
        indexs = download_financial_indexes(symbols="all", write_to_csv=True, base_path="hello")
        print(indexs)

    def test_get_history_indices(self):
        from oracle.services.tsetmc_indices import get_indices_history
        res = get_indices_history(date_from = "2022-01-01", date_to = "2022-04-01")
        print(res)


tr = Test_Service()
tr.test_get_index()
tr.test_get_live_askbid()
tr.test_get_history_indices()
