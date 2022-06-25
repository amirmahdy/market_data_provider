from django.test import TestCase
from oracle.models import Instrument
from oracle.utils import queue_detection

class Test_Service(TestCase):

    fixtures = ['instrumenttype', 'instrument']

    def test_instrument_queue_status(self):
        from oracle.utils import queue_detection

        market_data = {
           "tick_size":10,
           "bid_ask_first_row":{
              "best_buy_price":10800,
              "best_sell_price":10800,
              "best_sell_quantity":169475,
              "best_buy_quantity":109424,
              "no_best_buy":2,
              "no_best_sell":6
           },
           "symbol_isin":"IRO1BANK0001",
           "last_traded_price":10800,
           "closing_price":10710,
           "high_allowed_price":11760.0,
           "low_allowed_price":10440.0,
           "price_var":-2.7,
           "price_change":-300,
           "total_number_of_shares_traded":23226637,
           "closing_price_var":-3.51,
           "closing_price_change":-390,
           "order_max_size":"200000",
           "order_min_size":"1",
           "total_number_of_trades":1451,
           "total_trade_value":248847413210,
           "low_price":"8830",
           "high_price":"8900",
           "trade_date":"1401/01/22 09:08:43",
           "reference_price":11100,
           "basis_volume":10810811.0,
           "percent_of_basis_volume":"10900000",
           "fa_symbol_30":"سرمايه گذاري گروه توسعه ملي",
           "en_symbol":"BANK1",
           "first_traded_price":11050,
           "market_unit":"ETFStock",
           "market_code":"NO",
           "symbol_group_state":"1",
           "market_status":"مجاز",
           "market_status_text":"مجاز",
           "company_name":"سرمایه گذاری گروه توسعه ملی (وبانک)",
           "max_quantity_order":200000,
           "min_quantity_order":1,
           "symbol_fa":"وبانك"
        }

        askbid = [
            {
               "no_best_buy":1,
               "best_buy_price":9960,
               "best_sell_price":10180,
               "best_buy_quantity":1000,
               "best_sell_quantity":55937,
               "no_best_sell":3
            },
            {
               "no_best_buy":1,
               "best_buy_price":9910,
               "best_sell_price":10300,
               "best_buy_quantity":1000,
               "best_sell_quantity":46281,
               "no_best_sell":1
            },
            {
               "no_best_buy":2,
               "best_buy_price":9900,
               "best_sell_price":10390,
               "best_buy_quantity":1012,
               "best_sell_quantity":1000,
               "no_best_sell":1
            },
            {
               "no_best_buy":1,
               "best_buy_price":9710,
               "best_sell_price":10400,
               "best_buy_quantity":3549,
               "best_sell_quantity":100000,
               "no_best_sell":1
            },
            {
               "no_best_buy":1,
               "best_buy_price":9700,
               "best_sell_price":10450,
               "best_buy_quantity":516,
               "best_sell_quantity":56400,
               "no_best_sell":2
            }
        ]

        # Buy Queue
        market_data['high_allowed_price'] = 17660
        market_data['low_allowed_price'] = 16640
        market_data['last_traded_price'] = 17660

        askbid[0]['best_buy_price'] = 0
        askbid[1]['best_buy_price'] = 0
        askbid[2]['best_buy_price'] = 0
        askbid[3]['best_buy_price'] = 0
        askbid[4]['best_buy_price'] = 0
        askbid[0]['best_sell_price'] = 17660
        askbid[1]['best_sell_price'] = 17650
        askbid[2]['best_sell_price'] = 17600
        askbid[3]['best_sell_price'] = 17400
        askbid[4]['best_sell_price'] = 17350

        status = queue_detection(askbid, market_data)
        self.assertEqual(status, 'Is Buy Queue')

        # Sell_Queue
        market_data['high_allowed_price'] = 7690
        market_data['low_allowed_price'] = 7250
        market_data['last_traded_price'] = 17660

        askbid[0]['best_buy_price'] = 7250
        askbid[1]['best_buy_price'] = 7460
        askbid[2]['best_buy_price'] = 7470
        askbid[3]['best_buy_price'] = 7580
        askbid[4]['best_buy_price'] = 7600
        askbid[0]['best_sell_price'] = 0
        askbid[1]['best_sell_price'] = 0
        askbid[2]['best_sell_price'] = 0
        askbid[3]['best_sell_price'] = 0
        askbid[4]['best_sell_price'] = 0
        
        status = queue_detection(askbid, market_data)
        self.assertEqual(status, 'Is Sell Queue')

        # Near Buy_Queue
        market_data['high_allowed_price'] = 11260
        market_data['low_allowed_price'] = 10620
        market_data['last_traded_price'] = 11260

        askbid[0]['best_buy_price'] = 11260
        askbid[1]['best_buy_price'] = 0
        askbid[2]['best_buy_price'] = 0
        askbid[3]['best_buy_price'] = 0
        askbid[4]['best_buy_price'] = 0
        askbid[0]['best_sell_price'] = 11250
        askbid[1]['best_sell_price'] = 11240
        askbid[2]['best_sell_price'] = 11210
        askbid[3]['best_sell_price'] = 11200
        askbid[4]['best_sell_price'] = 11180
        
        status = queue_detection(askbid, market_data)
        self.assertEqual(status, 'Near Buy Queue')

        # Near Buy Queue 3

        market_data['high_allowed_price'] = 11260
        market_data['low_allowed_price'] = 10620
        market_data['last_traded_price'] = 11260

        askbid[0]['best_buy_price'] = 0
        askbid[1]['best_buy_price'] = 0
        askbid[2]['best_buy_price'] = 0
        askbid[3]['best_buy_price'] = 0
        askbid[4]['best_buy_price'] = 0
        askbid[0]['best_sell_price'] = 11250
        askbid[1]['best_sell_price'] = 11240
        askbid[2]['best_sell_price'] = 11210
        askbid[3]['best_sell_price'] = 11200
        askbid[4]['best_sell_price'] = 11180
        
        status = queue_detection(askbid, market_data)
        self.assertEqual(status, 'Near Buy Queue')

        # Near Sell Queue 3

        market_data['high_allowed_price'] = 11750
        market_data['low_allowed_price'] = 11070
        market_data['last_traded_price'] = 11080

        askbid[0]['best_buy_price'] = 11130
        askbid[1]['best_buy_price'] = 11140
        askbid[2]['best_buy_price'] = 11180
        askbid[3]['best_buy_price'] = 11190
        askbid[4]['best_buy_price'] = 11200
        askbid[0]['best_sell_price'] = 11080
        askbid[1]['best_sell_price'] = 11090
        askbid[2]['best_sell_price'] = 11100
        askbid[3]['best_sell_price'] = 11150
        askbid[4]['best_sell_price'] = 11200
        
        status = queue_detection(askbid, market_data)
        self.assertEqual(status, 'Near Sell Queue')