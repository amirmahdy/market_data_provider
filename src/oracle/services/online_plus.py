import threading
import traceback
from urllib.request import urlopen as _urlopen
from urllib.parse import urlparse as parse_url, urljoin, urlencode
import time
from oracle.data_type.instrument_market_data import InstrumentData
from oracle.models import Instrument
from morpheus.services.broadcast import broadcast_market_data, broadcast_askbid_data, broadcast_indices_data, \
    broadcast_indinst_data
import base64
import gzip
import ast
from mdp.log import Log

log = Log()

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
        instruments_list = Instrument.get_instruments()
        self.instruments = {instrument.isin: instrument for instrument in instruments_list}
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

        for isin in self.instruments:
            self.market_subscribe(isin)
            self.index_subscribe()
            self.askbid_subscribe(isin)

    def renew(self):
        self._ls_client.disconnect()
        time.sleep(5)
        self.__init__()

    def market_subscribe(self, isin):
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

        subscription.addlistener(self.on_market_update_rlc)
        sub_key = self._ls_client.subscribe(subscription)
        return sub_key

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
        res.update({key: float(item_update['values'][key]) for key in item_update['values'].keys()})
        # Cache data
        InstrumentData.update(res["SymbolISIN"], 'index', res)
        broadcast_indices_data(index_data=InstrumentData.get(res["SymbolISIN"], ref_group='index'))
        print(res)

    def verify(self, vals, res, key, local_key, type):
        if vals.get(key) is None:
            return res.get(local_key)
        return type(vals.get(key))

    def on_market_update_rlc(self, item_update):
        isin = item_update["name"][:12].upper()
        vals = item_update["values"]
        res = InstrumentData.get(isin=isin, ref_group='market')
        data = {
            "bid_ask_first_row": {
                "best_buy_price": self.verify(vals, res, "BestBuyLimitPrice_1", "best_buy_price", int),
                "best_sell_price": self.verify(vals, res, "BestSellLimitPrice_1", "best_sell_price", int),
                "best_sell_quantity": self.verify(vals, res, "BestSellLimitQuantity_1", "best_sell_quantity", int),
                "best_buy_quantity": self.verify(vals, res, "BestBuyLimitQuantity_1", "best_buy_quantity", int),
                "no_best_buy": self.verify(vals, res, "NumberOfOrdersAtBestBuy_1", "no_best_buy", int),
                "no_best_sell": self.verify(vals, res, "NumberOfOrdersAtBestSell_1", "no_best_sell", int),
            },
            "last_traded_price": self.verify(vals, res, "LastTradedPrice", "last_traded_price", int),
            "closing_price": self.verify(vals, res, "ClosingPrice", "closing_price", int),
            "price_var": self.verify(vals, res, "LastTradedPriceVarPercent", "price_var", float),
            "price_change": self.verify(vals, res, "LastTradedPriceVar", "price_change", int),
            "total_number_of_shares_traded": self.verify(vals, res, "TotalNumberOfSharesTraded",
                                                         "total_number_of_shares_traded", int),
            "closing_price_var": self.verify(vals, res, "ClosingPriceVarPercent", "closing_price_var", float),
            "closing_price_change": self.verify(vals, res, "ClosingPriceVar", "closing_price_change", int),
            "total_number_of_trades": self.verify(vals, res, "TotalNumberOfTrades", "total_number_of_trades", int),
            "total_trade_value": self.verify(vals, res, "TotalTradeValue", "total_trade_value", int),
            "low_price": self.verify(vals, res, "LowPrice", "low_price", int),
            "high_price": self.verify(vals, res, "HighPrice", "high_price", int),
            "trade_date": self.verify(vals, res, "TradeDate", "trade_date", str),
        }
        # Cache data
        InstrumentData.update(isin, ref_group='market', value=data)
        broadcast_market_data(isin=isin, market_data=InstrumentData.get(isin=isin, ref_group='market'))

        data_askbid = []
        for i in range(5):
            data_askbid.append(
                {
                    "best_sell_price": int(vals[f"BestSellLimitPrice_{i + 1}"]),
                    "best_sell_quantity": int(vals[f"BestSellLimitQuantity_{i + 1}"]),
                    "no_best_sell": int(vals[f"NumberOfOrdersAtBestSell_{i + 1}"]),
                    "best_buy_price": int(vals[f"BestBuyLimitPrice_{i + 1}"]),
                    "best_buy_quantity": int(vals[f"BestBuyLimitQuantity_{i + 1}"]),
                    "no_best_buy": int(vals[f"NumberOfOrdersAtBestBuy_{i + 1}"]),
                }
            )

        # Cache data
        InstrumentData.update(isin, ref_group='askbid', value=data_askbid)
        broadcast_askbid_data(isin=isin, askbid_data=InstrumentData.get(isin=isin, ref_group='askbid'))

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
            # Cache data_indinst
            InstrumentData.update(isin, ref_group='indinst', value=data_indinst)
            broadcast_indinst_data(isin=isin, indinst_data=InstrumentData.get(isin=isin, ref_group='indinst'))

        except Exception as e:
            log({"severity": "high", "path": "services/online_plus/on_market_update_rlc", "error": str(e)})

    def askbid_subscribe(self, isin):
        subscription = Subscription(
            mode="MERGE",
            items=[f"{isin.lower()}_marketdepth"],
            fields=[
                "data",
            ],
            adapter="MarketDepthAdapter",
        )

        subscription.addlistener(self.on_full_askbid_update_rlc)
        sub_key = self._ls_client.subscribe(subscription)
        return sub_key

    def on_full_askbid_update_rlc(self, item_update):
        isin = item_update["name"][:12].upper()
        vals = item_update["values"]
        coded_string = vals["data"]
        decoded = base64.b64decode(coded_string)
        decompressed_data = gzip.decompress(decoded)
        decompressed_data = decompressed_data.decode("UTF-8")
        data = ast.literal_eval(decompressed_data)

        InstrumentData.update(isin, ref_group='full_askbid', value=data)
