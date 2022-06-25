import asyncio
from datetime import datetime
import environ
import jdatetime
import requests
import websockets
from morpheus.services.broadcast import broadcast_market_data_async, broadcast_indinst_data_async, \
    broadcast_askbid_data_async, broadcast_indices_data_async
from oracle.models import Instrument

env = environ.Env()
RAYAN_SOCKET_RLC = env("RAYAN_SOCKET_RLC")
RAYAN_USERNAME = env("RAYAN_USERNAME")
RAYAN_PASSWORD = env("RAYAN_PASSWORD")
indices_info = [
    {
        "symbol_title": "شاخص 30 شركت بزرگ",
        "tse_id": "10523825119011581"
    },
    {
        "symbol_title": "شاخص50شركت فعالتر",
        "tse_id": "46342955726788357"
    },
    {
        "symbol_title": "شاخص صنعت",
        "tse_id": "43754960038275285"
    },
    {
        "symbol_title": "شاخص كل",
        "tse_id": "32097828799138957"
    },
    {
        "symbol_title": "شاخص قيمت (هم وزن)",
        "tse_id": "8384385859414435"
    },
    {
        "symbol_title": "شاخص كل فرابورس",
        "tse_id": "32097828799138957"
    },
]


def gregorian_to_jdate(item):
    year = int(item[:4])
    month = int(item[4:6])
    day = int(item[6:8])
    h = item[8:10]
    m = item[10:12]
    s = item[12:14]
    time = h + ":" + m + ":" + s
    jalili_date = jdatetime.date.fromgregorian(day=int(day), month=int(month), year=int(year)).strftime("%Y/%m/%d")
    date = jalili_date + " " + time
    return str(date)


async def rayan_websocket(rlc_auth_header, isins_list):
    while True:
        try:
            header = {
                "AUTH_WS": rlc_auth_header,
                "DEVICE_INFO": "Web"
            }
            async with websockets.connect(RAYAN_SOCKET_RLC, extra_headers=header) as client:
                for index in indices_info:
                    await client.send("1,MI.{}".format(str(index['tse_id'])))
                for isin in isins_list:
                    await client.send("1,MW.{}".format(str(isin)))
                while True:
                    try:
                        message_string = await client.recv()
                        message_string = message_string.split(",")
                        if message_string[0] == "MW":
                            isin = message_string[2]
                            best_limit_1 = str(message_string[20]).split(";")
                            best_limit_2 = str(message_string[21]).split(";")
                            best_limit_3 = str(message_string[22]).split(";")
                            best_limit_4 = str(message_string[39]).split(";")
                            best_limit_5 = str(message_string[40]).split(";")
                            price_change = float(message_string[9]) - float(message_string[13])
                            price_change_int = int(price_change)
                            price_var = float("%.2f" % ((price_change / float(message_string[13])) * 100))
                            closing_price_change = float(message_string[4]) - float(message_string[13])
                            closing_price_change_int = int(closing_price_change)
                            closing_price_var = float("%.2f" % ((closing_price_change / float(message_string[13])) * 100))
                            date = gregorian_to_jdate(message_string[19])
                            market_data = {
                                "bid_ask_first_row": {
                                    "best_buy_price": int(float(best_limit_1[2])),
                                    "best_sell_price": int(float(best_limit_1[6])),
                                    "best_sell_quantity": int(best_limit_1[5]),
                                    "best_buy_quantity": int(best_limit_1[1]),
                                    "no_best_buy": int(best_limit_1[3]),
                                    "no_best_sell": int(best_limit_1[7]),
                                },
                                "last_traded_price": int(float(message_string[9])),
                                "closing_price": int(float(message_string[4])),
                                "price_var": price_var,
                                "price_change": price_change_int,
                                "total_number_of_shares_traded": int(message_string[10]),
                                "closing_price_var": closing_price_var,
                                "closing_price_change": closing_price_change_int,
                                "total_number_of_trades": int(message_string[48]),
                                "total_trade_value": int(float(message_string[50])),
                                "low_price": int(float(message_string[12])),
                                "high_price": int(float(message_string[11])),
                                "trade_date": date,
                            }
                            askbid_data = [
                                {
                                    "best_buy_price": int(float(best_limit_1[2])),
                                    "best_sell_price": int(float(best_limit_1[6])),
                                    "best_sell_quantity": int(best_limit_1[5]),
                                    "best_buy_quantity": int(best_limit_1[1]),
                                    "no_best_buy": int(best_limit_1[3]),
                                    "no_best_sell": int(best_limit_1[7]),
                                },
                                {
                                    "best_buy_price": int(float(best_limit_2[2])),
                                    "best_sell_price": int(float(best_limit_2[6])),
                                    "best_sell_quantity": int(best_limit_2[5]),
                                    "best_buy_quantity": int(best_limit_2[1]),
                                    "no_best_buy": int(best_limit_2[3]),
                                    "no_best_sell": int(best_limit_2[7]),
                                },
                                {
                                    "best_buy_price": int(float(best_limit_3[2])),
                                    "best_sell_price": int(float(best_limit_3[6])),
                                    "best_sell_quantity": int(best_limit_3[5]),
                                    "best_buy_quantity": int(best_limit_3[1]),
                                    "no_best_buy": int(best_limit_3[3]),
                                    "no_best_sell": int(best_limit_3[7]),
                                },
                                {
                                    "best_buy_price": int(float(best_limit_4[2])),
                                    "best_sell_price": int(float(best_limit_4[6])),
                                    "best_sell_quantity": int(best_limit_4[5]),
                                    "best_buy_quantity": int(best_limit_4[1]),
                                    "no_best_buy": int(best_limit_4[3]),
                                    "no_best_sell": int(best_limit_4[7]),
                                },
                                {
                                    "best_buy_price": int(float(best_limit_5[2])),
                                    "best_sell_price": int(float(best_limit_5[6])),
                                    "best_sell_quantity": int(best_limit_5[5]),
                                    "best_buy_quantity": int(best_limit_5[1]),
                                    "no_best_buy": int(best_limit_5[3]),
                                    "no_best_sell": int(best_limit_5[7]),
                                }
                            ]
                            indinst_data = {
                                "symbol_isin": isin,
                                "ind_buy_volume": int(message_string[28]),
                                "ind_buy_number": int(message_string[26]),
                                "ind_sell_volume": int(message_string[32]),
                                "ind_sell_number": int(message_string[30]),
                                "ins_buy_volume": int(message_string[29]),
                                "ins_buy_number": int(message_string[27]),
                                "ins_sell_volume": int(message_string[33]),
                                "ins_sell_number": int(message_string[31]),
                            }
                            # InstrumentData.update(isin, ref_group='market', value=market_data)
                            await broadcast_market_data_async(isin=isin, market_data=market_data)
                            # InstrumentData.update(isin, ref_group='askbid', value=askbid_data)
                            await broadcast_askbid_data_async(isin=isin, askbid_data=askbid_data)
                            # InstrumentData.update(isin, ref_group='indinst', value=indinst_data)
                            await broadcast_indinst_data_async(isin=isin, indinst_data=indinst_data)
                        elif message_string[0] == "MI":
                            time = message_string[3]
                            date = str(datetime.now().strftime("%Y/%m/%d")) + "T" + time[:2] + ":" + time[2:4]
                            symbol_title = ""
                            for item in indices_info:
                                if item['tse_id'] == message_string[1]:
                                    symbol_title = item['symbol_title']
                                    break
                            indices_data = {
                                "DayOfEvent": date,
                                "IndexChanges": float(message_string[4]),
                                "LastIndexValue": float(message_string[2]),
                                "PercentVariation": float(message_string[5]),
                                "SymbolTitle": symbol_title,
                                "TseId": message_string[1],
                                "SymbolISIN": message_string[9]
                            }
                            # Cache data
                            # InstrumentData.update(message_string[9], 'index', indices_data)
                            await broadcast_indices_data_async(index_data=indices_data)
                        else:
                            pass

                    except Exception as e:
                        print(f'Failed in connecting RAYAN websocket (1): {e}')
                        break

        except Exception as e:
            time.sleep(10)
            print(f'Failed in connecting RAYAN websocket : {e}')


def rayan_login():
    captcha_url = "https://omsalgo96.irbroker.com/captcha"
    login_url = "https://omsalgo96.irbroker.com/api/v2/login"
    rlc_header_url = "https://omsalgo96.irbroker.com/api/v1/rlc/headers"

    s = requests.Session()
    headers_session = s.headers

    response = s.get(captcha_url, timeout=20, verify=False)

    customer_client_login_id = response.headers._store['client_login_id'][1]
    headers = {
        "content-type": "application/json",
        "device-type": '15',
        "broker-code": '405',
        "client_login_id": customer_client_login_id
    }
    headers_session.update(headers)
    data = {
        "username": RAYAN_USERNAME,
        "password": RAYAN_PASSWORD,
        "captcha": "",
        "otp": "",
    }
    response = s.post(login_url, json=data, headers=headers, timeout=20, verify=False)
    token = response.json()['authToken']
    hea = headers_session
    headers_session = {
        item: headers_session[item] for item in headers_session.keys()
        if
        item not in ["client_login_id"]
    }
    headers_session.update({
        "authToken": token
    })
    # try:
    response = s.get(rlc_header_url, timeout=20, verify=False)
    rlc_auth_header = str(response.json()['rlcAuthHeader']).replace('_', ',')
    return rlc_auth_header
    # except Exception as e:
    #     print("RLC AUTH HEADER not response")
    #     return False


def manage_rayan_webscoket():
    rlc_auth_header = rayan_login()
    isins_list = Instrument.get_instruments()
    isins_list = [isin.isin for isin in isins_list]
    asyncio.run(rayan_websocket(rlc_auth_header, isins_list))
