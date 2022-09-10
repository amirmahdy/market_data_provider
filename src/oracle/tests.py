from django.test import TestCase


class Test_Service(TestCase):

    def test_get_live_askbid(self):
        from oracle.services.tsetmc_askbid import get_live_askbid
        from oracle.models import Instrument
        instruments = Instrument.get_instrument("IRO1BANK0001")[0]
        res = get_live_askbid(instruments.tse_id)
        self.assertEqual(type(res), list)
        return True

    def test_get_tse_instrument_data(self):
        from oracle.models import Instrument
        from oracle.services.tsetmc_market import get_tse_instrument_data
        instruments = Instrument.get_instrument("IRO1BANK0001")[0]

        res = get_tse_instrument_data(instruments)
        print(res)


TS = Test_Service()
TS.test_get_tse_instrument_data()
