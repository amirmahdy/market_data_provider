from django.test import TestCase, RequestFactory
from .views.trades_history import TradeDataAPIView
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
