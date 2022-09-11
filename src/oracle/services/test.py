import os
import django
from django.test import TestCase

from mdp.utils import create_csv
from oracle.services.tsetmc_trades import get_tick_data

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mdp.settings")
django.setup()


class TestService(TestCase):

    def test_get_kline(self):
        from oracle.services.tsetmc_trades import get_kline
        import environ
        from oracle.models import Instrument

        env = environ.Env()
        instruments = Instrument.get_instruments()

        res = get_kline("20220101", "20220103", instruments[0].tse_id, env("TSETMC_USERNAME"), env("TSETMC_PASSWORD"))
        print(res)

    def test_get_tick_data(self):
        from oracle.models import Instrument
        instruments = Instrument.get_instruments()
        print("instrument isin-------------", instruments[0].tse_id)
        res = get_tick_data(instruments[0].tse_id, "20220529")
        print(res)

    def test_task_kline(self):
        from oracle.tasks import trade_data_yesterday_update
        res = trade_data_yesterday_update()
        print(res)

    def test_get_live_askbid(self):
        from oracle.models import Instrument
        from oracle.services.tsetmc_askbid import get_live_askbid
        instruments = Instrument.get_instrument("IRO1BANK0001")
        res = get_live_askbid(instruments[0])
        print(res)

    def test_get_history_askbid(self):
        from oracle.models import Instrument
        from oracle.services.tsetmc_askbid import get_askbid_history
        instruments = Instrument.get_instrument("IRO1BANK0001")
        res = get_askbid_history(instruments[0].tse_id, "20220517")
        sym = 'bank1'
        create_csv('./data/askbid/' + sym + "/" + '20220517' + ".csv", res,
                   fieldnames=["time", "buy_price_1", "buy_volume_1", "buy_count_1", "sell_price_1",
                               "sell_volume_1", "sell_count_1", "buy_price_2", "buy_volume_2", "buy_count_2",
                               "sell_price_2", "sell_volume_2", "sell_count_2", "buy_price_3", "buy_volume_3",
                               "buy_count_3", "sell_price_3", "sell_volume_3", "sell_count_3", "buy_price_4",
                               "buy_volume_4", "buy_count_4", "sell_price_4", "sell_volume_4", "sell_count_4",
                               "buy_price_5", "buy_volume_5", "buy_count_5", "sell_price_5", "sell_volume_5",
                               "sell_count_5"], frmt="w+")
        print(res)

    def test_get_tse_instrument_data(self):
        from oracle.models import Instrument
        from oracle.services.tsetmc_market import get_tse_instrument_data
        instruments = Instrument.get_instrument("IRO1BANK0001")
        get_tse_instrument_data(instruments[0])

    def test_get_index(self):
        from pytse_client.download import download_financial_indexes
        indexs = download_financial_indexes(symbols="all", write_to_csv=True, base_path="hello")
        print(indexs)

    def test_get_tse_instrument_data(self):
        from oracle.models import Instrument
        instruments = Instrument.get_instrument("IRO1SMAZ0001")[0]
        from oracle.services.tsetmc_market import get_tse_instrument_data
        res = get_tse_instrument_data(instruments)
        print(res)

    def test_get_history_indices(self):
        from oracle.services.tsetmc_indices import get_indices_history
        res = get_indices_history(date_from="2022-01-01", date_to="2022-04-01")
        print(res)

    def test_get_indices_live(self):
        from oracle.services.tsetmc_indices import get_indices_live
        res = get_indices_live()
        print(res)

    def test_get_tse_instrument_data(self):
        from oracle.models import Instrument
        instruments = Instrument.get_instrument("IRO1SMAZ0001")[0]
        from oracle.services.tsetmc_market import get_tse_instrument_data
        res = get_tse_instrument_data(instruments)
        print(res)

    def test_market_data_update(self):
        from oracle.tasks import market_data_update
        market_data_update()


tr = TestService()
tr.test_get_indices_live()
