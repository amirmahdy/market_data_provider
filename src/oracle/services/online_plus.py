import threading
import traceback
from urllib.request import urlopen as _urlopen
from urllib.parse import urlparse as parse_url, urljoin, urlencode
from datetime import datetime
import time
from oracle.data_type.instrument_market_data import InstrumentData
from oracle.models import Instrument

CONNECTION_URL_PATH = "lightstreamer/create_session.txt"
BIND_URL_PATH = "lightstreamer/bind_session.txt"
CONTROL_URL_PATH = "lightstreamer/control.txt"
OP_ADD = "add"
OP_DELETE = "delete"
OP_DESTROY = "destroy"
PROBE_CMD = "PROBE"
END_CMD = "END"
LOOP_CMD = "LOOP"
ERROR_CMD = "ERROR"
SYNC_ERROR_CMD = "SYNC ERROR"
OK_CMD = "OK"


class Subscription(object):
    def __init__(self, mode, items, fields, adapter=""):
        self.item_names = items
        self._items_map = {}
        self.field_names = fields
        self.adapter = adapter
        self.mode = mode
        self.snapshot = "true"
        self._listeners = []

    def _decode(self, value, last):
        if value == "$":
            return ""
        elif value == "#":
            return None
        elif not value:
            return last
        elif value[0] in "#$":
            value = value[1:]

        return value

    def addlistener(self, listener):
        self._listeners.append(listener)

    def notifyupdate(self, item_line):
        toks = item_line.rstrip("\r\n").split("|")
        undecoded_item = dict(list(zip(self.field_names, toks[1:])))
        item_pos = int(toks[0])
        curr_item = self._items_map.get(item_pos, {})
        self._items_map[item_pos] = dict(
            [
                (k, self._decode(v, curr_item.get(k)))
                for k, v in list(undecoded_item.items())
            ]
        )
        item_info = {
            "pos": item_pos,
            "name": self.item_names[item_pos - 1],
            "values": self._items_map[item_pos],
        }
        for on_item_update in self._listeners:
            on_item_update(item_info)


class LSClient(object):
    def __init__(self, base_url, adapter_set="", user="", password=""):
        self._base_url = parse_url(base_url)
        self._adapter_set = adapter_set
        self._user = user
        self._password = password
        self._session = {}
        self._subscriptions = {}
        self._current_subscription_key = 0
        self._stream_connection = None
        self._stream_connection_thread = None
        self._bind_counter = 0

    def _url_encode(self, params):
        return urlencode(params).encode("utf-8")

    def _iteritems(self, d):
        return iter(d.items())

    def _encode_params(self, params):
        return self._url_encode(
            dict([(k, v) for (k, v) in self._iteritems(params) if v])
        )

    def _call(self, base_url, url, params):
        url = urljoin(base_url.geturl(), url)
        body = self._encode_params(params)
        print("Making a request to <%s> with body <%s>", url, body)
        return _urlopen(url, data=body)

    def _set_control_link_url(self, custom_address=None):
        if custom_address is None:
            self._control_url = self._base_url
        else:
            parsed_custom_address = parse_url("//" + custom_address)
            self._control_url = parsed_custom_address._replace(
                scheme=self._base_url[0])

    def _control(self, params):
        params["LS_session"] = self._session["SessionId"]
        response = self._call(self._control_url, CONTROL_URL_PATH, params)
        decoded_response = response.readline().decode("utf-8").rstrip()
        print("Server response: <%s>", decoded_response)
        return decoded_response

    def _read_from_stream(self):
        line = self._stream_connection.readline().decode("utf-8").rstrip()
        return line

    def connect(self):
        print("Opening a new session to <%s>", self._base_url.geturl())
        self._stream_connection = self._call(
            self._base_url,
            CONNECTION_URL_PATH,
            {
                "LS_op2": "create",
                "LS_cid": "pcYgxn8m8 feOojyA1T681f3g2.pz479mDv",
                "LS_adapter_set": self._adapter_set,
                "LS_user": self._user,
                "LS_password": self._password,
            },
        )
        stream_line = self._read_from_stream()
        self._handle_stream(stream_line)

    def bind(self):
        print("Binding to <%s>", self._control_url.geturl())
        self._stream_connection = self._call(
            self._control_url, BIND_URL_PATH, {
                "LS_session": self._session["SessionId"]}
        )

        self._bind_counter += 1
        stream_line = self._read_from_stream()
        self._handle_stream(stream_line)
        print("Bound to <%s>", self._control_url.geturl())

    def _handle_stream(self, stream_line):
        if stream_line == OK_CMD:
            print("Successfully connected to <%s>", self._base_url.geturl())
            print("Starting to handling real-time stream")
            # Parsing session inkion
            while 1:
                next_stream_line = self._read_from_stream()
                if next_stream_line:
                    session_key, session_value = next_stream_line.split(":", 1)
                    self._session[session_key] = session_value
                else:
                    break
            self._set_control_link_url(self._session.get("ControlAddress"))
            self._stream_connection_thread = threading.Thread(
                name="StreamThread-{0}".format(self._bind_counter), target=self._receive
            )
            self._stream_connection_thread.setDaemon(True)
            self._stream_connection_thread.start()
            print("Started handling of real-time stream")
        else:
            lines = self._stream_connection.readlines()
            lines.insert(0, stream_line)
            print(
                "\nServer response error: \n%s", "".join(
                    [str(line) for line in lines])
            )
            raise IOError()

    def _join(self):
        if self._stream_connection_thread:
            print("Waiting for thread to terminate")
            self._stream_connection_thread.join()
            self._stream_connection_thread = None
            print("Thread terminated")

    def disconnect(self):
        if self._stream_connection is not None:
            print("Closing session to <%s>", self._base_url.geturl())
            server_response = self._control({"LS_op": OP_DESTROY})
            self._join()
            print("Closed session to <%s>", self._base_url.geturl())
        else:
            print("No connection to Lightstreamer")

    def subscribe(self, subscription):
        self._current_subscription_key += 1
        self._subscriptions[self._current_subscription_key] = subscription
        print("Making a new subscription request")
        server_response = self._control(
            {
                "LS_table": self._current_subscription_key,
                "LS_op": OP_ADD,
                "LS_data_adapter": subscription.adapter,
                "LS_mode": subscription.mode,
                "LS_schema": " ".join(subscription.field_names),
                "LS_id": " ".join(subscription.item_names),
            }
        )
        if server_response == OK_CMD:
            print("Successfully subscribed ")
        else:
            print("Subscription error")
        return self._current_subscription_key

    def unsubscribe(self, subcription_key):
        print("Making an unsubscription request")
        if subcription_key in self._subscriptions:
            server_response = self._control(
                {"LS_Table": subcription_key, "LS_op": OP_DELETE}
            )

            if server_response == OK_CMD:
                del self._subscriptions[subcription_key]
                print("Successfully unsubscribed")
            else:
                print("Unsubscription error")
        else:
            print("No subscription key %s found!", subcription_key)

    def _forward_update_message(self, update_message):
        print("Received update message: <%s>", update_message)
        try:
            tok = update_message.split(",", 1)
            table, item = int(tok[0]), tok[1]
            if table in self._subscriptions:
                self._subscriptions[table].notifyupdate(item)
            else:
                print("No subscription found!")
        except Exception:
            print(traceback.format_exc())

    def _receive(self):
        rebind = False
        receive = True
        while receive:
            print("Waiting for a new message")
            try:
                message = self._read_from_stream()
                print("Received message: <%s>", message)
                if not message.strip():
                    message = None
            except Exception:
                print("Communication error")
                print(traceback.format_exc())
                message = None

            if message is None:
                receive = False
                print("No new message received")
            elif message == PROBE_CMD:
                print("PROBE message")
            elif message.startswith(ERROR_CMD):
                receive = False
                print("ERROR")
            elif message.startswith(LOOP_CMD):
                print("LOOP")
                receive = False
                rebind = True
            elif message.startswith(SYNC_ERROR_CMD):
                print("SYNC ERROR")
                receive = False
            elif message.startswith(END_CMD):
                print("Connection closed by the server")
                receive = False
            elif message.startswith("Preamble"):
                print("Preamble")
            else:
                self._forward_update_message(message)

        if not rebind:
            print(
                "No rebind to <%s>, clearing internal session data",
                self._base_url.geturl(),
            )
            # Clear internal data structures for session
            # and subscriptions management.
            self._stream_connection = None
            self._session.clear()
            self._subscriptions.clear()
            self._current_subscription_key = 0
        else:
            print("Binding to this active session")
            self.bind()


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if "Instance" not in instances:
            instances["Instance"] = class_(*args, **kwargs)
        return instances["Instance"]

    return getinstance


@singleton
class LS_Class:
    def __init__(self):
        self.instruments = Instrument.get_instruments()
        self._ls_client = LSClient(
            "https://push2v7.etadbir.com/",
            "STOCKLISTDEMO_REMOTE",
            user="132&bmi20213631",
            password="132",
        )
        try:
            self._ls_client.connect()
        except Exception as e:
            print("Unable to connect to Lightstreamer Server")
            print(traceback.format_exc())

        # instruments_raw = ["IRO1BANK0001", "IRO1PARK0001"]
        for ins_raw in self.instruments:
            self.isin_subscribe(ins_raw)
            self.index_subscribe()

    def renew(self):
        self._ls_client.disconnect()
        time.sleep(5)
        self.__init__()

    def isin_subscribe(self, isin):
        subscription = Subscription(
            mode="MERGE",
            items=[f"{isin.lower()}_lightrlc"],
            fields=[
                "HighPrice",
                "LowPrice",
                "TradeDate",
                "YesterdayPrice",
                "LastTradedPrice",
                "LastTradedPriceVar",
                "LastTradedPriceVarPercent",
                "TotalNumberOfSharesTraded",
                "ClosingPrice",
                "ClosingPriceVar",
                "BestBuyLimitPrice_1",
                "BestSellLimitPrice_1",
                "BestBuyLimitQuantity_1",
                "BestSellLimitQuantity_1",
                "NumberOfOrdersAtBestBuy_1",
                "NumberOfOrdersAtBestSell_1",
                "BestBuyLimitPrice_2",
                "BestSellLimitPrice_2",
                "BestBuyLimitQuantity_2",
                "BestSellLimitQuantity_2",
                "NumberOfOrdersAtBestBuy_2",
                "NumberOfOrdersAtBestSell_2",
                "BestBuyLimitPrice_3",
                "BestSellLimitPrice_3",
                "BestBuyLimitQuantity_3",
                "BestSellLimitQuantity_3",
                "NumberOfOrdersAtBestBuy_3",
                "NumberOfOrdersAtBestSell_3",
                "BestBuyLimitPrice_4",
                "BestSellLimitPrice_4",
                "BestBuyLimitQuantity_4",
                "BestSellLimitQuantity_4",
                "NumberOfOrdersAtBestBuy_4",
                "NumberOfOrdersAtBestSell_4",
                "BestBuyLimitPrice_5",
                "BestSellLimitPrice_5",
                "BestBuyLimitQuantity_5",
                "BestSellLimitQuantity_5",
                "NumberOfOrdersAtBestBuy_5",
                "NumberOfOrdersAtBestSell_5",
                "ClosingPriceVarPercent",
                "BasisVolume",
                "LowAllowedPrice",
                "HighAllowedPrice",
                "SymbolStateId",
                "InstrumentCode",
                "SymbolHighLimit",
                "SymbolNoteLowLimit",
                "FirstTradedPrice",
                "PreClosingPrice",
                "CompanyName",
                "TotalNumberOfTrades",
                "TotalTradeValue",
                "IndInstTrade_Individual_BuyValue",
                "IndInstTrade_Individual_BuyVolume",
                "IndInstTrade_Individual_BuyNumber",
                "IndInstTrade_Individual_SellValue",
                "IndInstTrade_Individual_SellVolume",
                "IndInstTrade_Individual_SellNumber",
                "IndInstTrade_Institutional_BuyValue",
                "IndInstTrade_Institutional_BuyVolume",
                "IndInstTrade_Institutional_BuyNumber",
                "IndInstTrade_Institutional_SellVolume",
                "IndInstTrade_Institutional_SellValue",
                "IndInstTrade_Institutional_SellNumber",
            ],
            adapter="TadbirLightRLC",
        )

        subscription.addlistener(self.on_public_update_rlc)
        sub_key = self._ls_client.subscribe(subscription)
        return sub_key

    def isin_unsubscribe(self, sub_key):
        self._ls_client.unsubscribe(sub_key)
        return True

    def index_subscribe(self):
        subscription = Subscription(
            mode="MERGE",
            items=["irx6xtpi0006_lightrlc",  # Market whole Index
                   "irxzxoci0006_lightrlc",  # Fara Bourse Index
                   "irx6xslc0006_lightrlc",  # 50 Top Index
                   "irx6xs300006_lightrlc",  # 30 Top Index
                   "irxyxtpi0026_lightrlc"  # Same-Price Index
                   ],
            fields=[
                "LastIndexValue",
                "PercentVariation",
                "IndexChanges",
            ],
            adapter="TadbirLightRLC",
        )

        subscription.addlistener(self.on_index_update_rlc)
        sub_key = self._ls_client.subscribe(subscription)
        return sub_key

    def on_index_update_rlc(self, item_update):
        res = {"SymbolISIN": item_update['name'].upper()[:12], }
        res.update(item_update['values'])
        print(res)

    def on_public_update_rlc(self, item_update):
        isin = item_update["name"][:12].upper()
        vals = item_update["values"]
        local_vals = self.instruments[isin]

        data = {
            "first_symbol_state": local_vals["first_symbol_state"],
            "second_symbol_state": local_vals["second_symbol_state"],
            "max_percent_change": local_vals["max_percent_change"],
            "max_low_percent_change": local_vals["max_low_percent_change"],
            "theoretical_openning_price": local_vals["theoretical_openning_price"],
            "is_caution": local_vals["is_caution"],
            "price_tick_size": local_vals["price_tick_size"],
            "bid_ask_first_row": {
                "best_buy_price": vals["BestBuyLimitPrice_1"],
                "best_sell_price": vals["BestSellLimitPrice_1"],
                "best_sell_quantity": vals["BestSellLimitQuantity_1"],
                "best_buy_quantity": vals["BestBuyLimitQuantity_1"],
                "no_best_buy": vals["NumberOfOrdersAtBestBuy_1"],
                "no_best_sell": vals["NumberOfOrdersAtBestSell_1"],
            },
            "symbol_isin": isin,
            "last_traded_price": vals["LastTradedPrice"],
            "closing_price": vals["ClosingPrice"],
            "high_allowed_price": vals["HighAllowedPrice"],
            "low_allowed_price": vals["LowAllowedPrice"],
            "price_var": vals["LastTradedPriceVarPercent"],
            "price_change": vals["LastTradedPriceVar"],
            "total_number_of_shares_traded": vals["TotalNumberOfSharesTraded"],
            "company_name": local_vals["company_name"],
            "en_company_name": local_vals["en_company_name"],
            "closing_price_var": vals["ClosingPriceVarPercent"],
            "closing_price_change": vals["ClosingPriceVar"],
            "max_quantity_order": local_vals["max_quantity_order"],
            "min_quantity_order": local_vals["min_quantity_order"],
            "total_number_of_trades": vals["TotalNumberOfTrades"],
            "total_trade_value": vals["TotalTradeValue"],
            "low_price": vals["LowPrice"],
            "high_price": vals["HighPrice"],
            "trade_date": vals["TradeDate"],
            "reference_price": vals["YesterdayPrice"],
            "basis_volume": vals["BasisVolume"],
            "percent_of_basis_volume": vals["BasisVolume"],
            "symbol_fa": local_vals["symbol_fa"],
            "symbol_en": local_vals["symbol_en"],
            "first_traded_price": vals["FirstTradedPrice"],
            "market_unit": "ETFStock",
            "market_code": local_vals["market_code"],
            "symbol_group_state": vals["SymbolStateId"],
            "symbol_group_code": local_vals["symbol_group_code"],
            "unit_count": local_vals["unit_count"],
            "sector_code": local_vals["sector_code"],
            "tomorrow_high_allowed_price": local_vals["tomorrow_high_allowed_price"],
            "tomorrow_low_allowed_price": local_vals["tomorrow_low_allowed_price"],
            "market_status": "ALLOWED",
            "market_status_text": "\u0645\u062c\u0627\u0632",
        }

        # Cache data
        InstrumentData.update(
            isin, ref_group='market', value=data)
        data_askbid = []

        for i in range(5):
            data_askbid.append(
                {
                    "order_side": "SELL",
                    "price": vals[f"BestSellLimitPrice_{i + 1}"],
                    "quantity": vals[f"BestSellLimitQuantity_{i + 1}"],
                    "count": vals[f"NumberOfOrdersAtBestSell_{i + 1}"],
                    "type": "MARKET",
                }
            )
            data_askbid.append(
                {
                    "order_side": "BUY",
                    "price": vals[f"BestBuyLimitPrice_{i + 1}"],
                    "quantity": vals[f"BestBuyLimitQuantity_{i + 1}"],
                    "count": vals[f"NumberOfOrdersAtBestBuy_{i + 1}"],
                    "type": "MARKET",
                }
            )

        print(data_askbid)
        try:
            data_indinst = {
                "symbol_isin": isin,
                "ind_buy_volume": int(vals["IndInstTrade_Individual_BuyVolume"]),
                "ind_buy_number": int(vals["IndInstTrade_Individual_BuyNumber"]),
                "ind_buy_value": int(vals["IndInstTrade_Individual_BuyValue"]),
                "ind_sell_volume": int(vals["IndInstTrade_Individual_SellVolume"]),
                "ind_sell_number": int(vals["IndInstTrade_Individual_SellNumber"]),
                "ind_sell_value": int(vals["IndInstTrade_Individual_SellValue"]),
                "ins_buy_volume": int(vals["IndInstTrade_Institutional_BuyVolume"]),
                "ins_buy_number": int(vals["IndInstTrade_Institutional_BuyNumber"]),
                "ins_buy_value": int(vals["IndInstTrade_Institutional_BuyValue"]),
                "ins_sell_volume": int(vals["IndInstTrade_Institutional_SellVolume"]),
                "ins_sell_number": int(vals["IndInstTrade_Institutional_SellNumber"]),
                "ins_sell_value": int(vals["IndInstTrade_Institutional_SellValue"]),
            }

            print(data_indinst)
        except Exception as e:
            pass
