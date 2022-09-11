from morpheus.views.trades_history import TradeDataAPIView
from django.test import TestCase, RequestFactory
import os
import django
from oracle.services.tsetmc_indices import get_indices_live
from oracle.services.tsetmc_indinst import get_live_indinst

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mdp.settings")
django.setup()


# Create your tests here.


class MorpheusViewsTestCase(TestCase):
    fixtures = ['instrument']

    def test_today_trades_view(self):
        from oracle.tasks import market_data_update

        # Cache market data as it's happening in tasks
        market_data_update()

        factory = RequestFactory()
        request = factory.get(path='/morpheus/trades_history',
                              data={'isin': 'IRO1BANK0001'})
        response = TradeDataAPIView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_log_splunk(self):
        from mdp.log import Log
        log = Log()
        log("Hello from app")

    def test_initial_indices(self):
        response = get_indices_live()
        print(response)


test = MorpheusViewsTestCase()
# test.test_log_splunk()
test.test_initial_indices()
