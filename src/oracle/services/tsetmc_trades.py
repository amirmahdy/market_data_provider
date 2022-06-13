import requests
from datetime import datetime
import re
import json

TICK_BASE_URL = "http://cdn.tsetmc.com/api/Trade/GetTradeHistory/{isin}/{cur_date}/true"
TRADE_HISTORY_TODAY_URL = "http://tsetmc.com/tsev2/data/TradeDetail.aspx?i={tse_isin}"
TRADE_HISTORY_YESTERDAY_URL = "http://cdn.tsetmc.com/api/Trade/GetTradeHistory/{tse_isin}/{date}/false"
GATHER_ONE_DAY_URL = "http://service.tsetmc.com/WebService/TsePublicV2.asmx?op=InstTrade"


def get_trades(tse_isin: str, day=None):
    if day is None:
        today = datetime.now().strftime('%Y-%m-%dT')
        url = TRADE_HISTORY_TODAY_URL.format(tse_isin=tse_isin)
        session = requests.Session()
        resp = session.get(url).text
        rgx = (
            "<row>[\s|\r]*<cell>\d*\.?\d*</cell>"
            "[\s|\r]*<cell>(\d*\:\d*\:\d*)</cell>"
            "[\s|\r]*<cell>(\d*\.?\d*)</cell>"
            "[\s|\r]*<cell>(\d*\.?\d*)</cell>"
            "[\s|\r]*</row>"
        )
        all_trades = re.findall(rgx, resp)
        all_trades_dc = []
        for trade in all_trades:
            all_trades_dc.append({"t": (today + trade[0]), "p": int(float(trade[2])), "q": int(float(trade[1]))})
        return all_trades_dc

    else:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Host": "cdn.tsetmc.com",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.5",
            "Upgrade-Insecure-Requests": "1"
        }
        tse_full_data = requests.get(TRADE_HISTORY_YESTERDAY_URL.format(tse_isin=tse_isin, date=day), headers=headers)
        tse_res = json.loads(tse_full_data.text)
        new_history_list = []
        day = datetime.strptime(day, '%Y%m%d').strftime('%Y-%m-%dT')
        for item in tse_res['tradeHistory']:
            heven = ("%06d" % item["hEven"])
            h = heven[0:2] + ":" + heven[2:4] + ":" + heven[4:6]
            new_dict = {
                "t": day + h,  # YYYY-MM-DDTmm:hh:ss
                "q": int(item['qTitTran']),
                "p": int(item['pTran']),
            }
            new_history_list.append(new_dict)
        new_history_list.reverse()
        return new_history_list


def get_kline(from_date, to_date, tse_isin, val_user, val_pass):
    headers = {'content-type': 'text/xml', 'SOAPAction': 'http://tsetmc.com/InstTrade'}
    body = """<?xml version="1.0" encoding="utf-8"?>
                            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                              <soap:Body>
                                <InstTrade xmlns="http://tsetmc.com/">
                                  <UserName>{0}</UserName>
                                  <Password>{1}</Password>
                                  <Inscode>{2}</Inscode>
                                  <DateFrom>{3}</DateFrom>
                                  <DateTo>{4}</DateTo>
                                </InstTrade>
                              </soap:Body>
                            </soap:Envelope>""".format(val_user, val_pass, tse_isin, from_date, to_date)
    session = requests.Session()
    response = session.post(GATHER_ONE_DAY_URL, data=body, headers=headers)
    xml_raw = response.content.decode('utf-8')
    xml_data = re.findall(
        '<DEven>(\d*\.?\d*)<\/DEven>[\s|\r]*'
        '<HEven>(\d*\.?\d*)[\s|\r]*<\/HEven>[\s|\r]*'
        '<PClosing>(\d*\.?\d*)<\/PClosing>[\s|\r]*'
        '<IClose>(\d*\.?\d*)<\/IClose>[\s|\r]*'
        '<YClose>(\d*\.?\d*)<\/YClose>[\s|\r]*'
        '<PDrCotVal>(\d*\.?\d*)<\/PDrCotVal>[\s|\r]*'
        '<ZTotTran>(\d*\.?\d*)<\/ZTotTran>[\s|\r]*'
        '<QTotTran5J>(\d*\.?\d*)<\/QTotTran5J>[\s|\r]*'
        '<QTotCap>(\d*\.?\d*)<\/QTotCap>[\s|\r]*'
        '<PriceChange>(\-?\d*\.?\d*)<\/PriceChange>[\s|\r]*'
        '<PriceMin>(\d*\.?\d*)<\/PriceMin>[\s|\r]*'
        '<PriceMax>(\d*\.?\d*)<\/PriceMax>[\s|\r]*'
        '<PriceYesterday>(\d*\.?\d*)<\/PriceYesterday>[\s|\r]*'
        '<PriceFirst>(\d*\.?\d*)<\/PriceFirst>[\s|\r]*', xml_raw)

    if xml_data == []:
        return
    xml_row = []
    for xml_ins in xml_data:
        xml_row.append([xml_ins[0] + ' 00:00', "{:.0f}".format(float(xml_ins[13])),
                        "{:.0f}".format(float(xml_ins[11])), "{:.0f}".format(float(xml_ins[10])),
                        "{:.0f}".format(float(xml_ins[2])), "{:.0f}".format(float(xml_ins[7]))])
    return xml_row


def get_tick_data(isin, cur_date):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
    }
    tse_full_data = requests.get(TICK_BASE_URL.format(isin=isin, cur_date=cur_date), headers=headers)
    tse_res = json.loads(tse_full_data.text)
    new_history_list = []
    for item in tse_res['tradeHistory']:
        heven = ("%06d" % item["hEven"])
        h = heven[0:2] + ":" + heven[2:4] + ":" + heven[4:6]
        new_dict = [h, int(item['qTitTran']), int(item['pTran']), "D", "@", 0]
        new_history_list.append(new_dict)
    new_history_list.reverse()
    return new_history_list
