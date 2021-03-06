import os
import django
from django.test import TestCase

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mdp.settings")
django.setup()


class Test_Redis(TestCase):
    def test_redis(self):
        from oracle.data_type.instrument_market_data import InstrumentData
        res = InstrumentData.get(isin="IRO1BANK0001", ref_group="market")
        InstrumentData.update("IRO1BANK0001", "market", {"dat": 32})
        print(res)

    def test_get_instrument_list(self):
        from oracle.models import Instrument
        instruments = Instrument.get_instruments()
        print(instruments)

    def test_task_update_tsetmc_instrument_market(self):
        from oracle.tasks import market_data_update
        mup = market_data_update()

    def test_tsetmc_speed_limit(self):
        from oracle.tasks import market_data_update
        import time
        start = time.time()
        market_data_update()
        print(time.time() - start)


tr = Test_Redis()
tr.test_redis()
