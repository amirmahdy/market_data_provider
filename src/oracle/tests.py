from django.test import TestCase


class Test_Service(TestCase):

    def test_get_live_askbid(self):
        from oracle.services.tsetmc_askbid import get_live_askbid
        from oracle.models import Instrument
        instruments = Instrument.get_instrument("IRO1BANK0001")[0]
        res = get_live_askbid(instruments.tse_id)
        self.assertEqual(type(res), list)
        return True


TS = Test_Service()
TS.test_get_live_askbid()
