from django.test import TestCase


class Test_Service(TestCase):

    def test_get_live_askbid(self):
        from oracle.services.tsetmc_askbid import get_live_askbid
        from oracle.models import Instrument
        instruments = Instrument.get_instrument("IRO1BANK0001")[0]
        res = get_live_askbid(instruments)
        self.assertEqual(type(res), list)
        return True

    def test_get_tse_instrument_data(self):
        from oracle.models import Instrument
        from oracle.services.tsetmc_market import get_tse_instrument_data
        instruments = Instrument.get_instrument("IRO1BANK0001")[0]
        res = get_tse_instrument_data(instruments)
        print(res)

    def test_get_live_indinst(self):
        from oracle.models import Instrument
        from oracle.services.tsetmc_indinst import get_live_indinst
        instruments = Instrument.get_instrument("IRB3TB750291")[0]
        res = get_live_indinst(instruments)
        print(res)

    def test_get_indices_live(self):
        from oracle.services.tsetmc_indices import get_indices_live
        res = get_indices_live()
        print(res)

    def test_task_instrument_update(self):
        from oracle.tasks import instrument_update
        instrument_update()
