import requests
import re

BASE_URL = 'http://www.tsetmc.com/Loader.aspx?Partree=151315&Flow=1'
INDEX_URL = 'http://cdn.tsetmc.com/api/Index/GetIndexB1LastAll/All/1'

indices = {"10523825119011581": "IRX6XS300006", "43754960038275285": "IRX6XSNT0006",
           "32097828799138957": "IRX6XTPI0006", "8384385859414435": "IRXYXTPI0026",
           "46342955726788357": "IRX6XSLC0006"}

INDEX_LIST = ["10523825119011581", "43754960038275285",
              "32097828799138957", "8384385859414435",
              "46342955726788357"]

regex = '<tr><td><a.*{index}">(.*)<\\/a>.*\\s\\n<td>(.*)<\\/td>\\s\\n<td>(.*)<\\/td>\\s\\n<td>.*>(.*)<.*<\\/td>\\s\\n<td>.*>(.*)<.*<\\/td>'


def _f(flt):
    chars_to_remove = [',', '(', ')']
    return float(''.join([c for c in flt if c not in chars_to_remove]))



def get_indices_live():
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
               "Host": "cdn.tsetmc.com",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "en-US,en;q=0.5",
               "Upgrade-Insecure-Requests": "1"
               }
    response = requests.get(INDEX_URL, headers=headers).json()['indexB1']
    index_list = []
    for idx in response:
        if idx['insCode'] in INDEX_LIST:
            index_dict = {
                "IndexChanges": idx['indexChange'],
                "LastIndexValue": idx['xDrNivJIdx004'],
                "PercentVariation": idx['xVarIdxJRfV'],
                "SymbolTitle": idx['lVal30'],
                "SymbolISIN": indices[idx['insCode']],
            }
            index_list.append(index_dict)
    return index_list
