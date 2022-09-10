import requests
import re

BASE_URL = 'http://www.tsetmc.com/Loader.aspx?Partree=151315&Flow=1'
indices = {"10523825119011581": "IRX6XS300006", "43754960038275285": "IRX6XSNT0006",
           "32097828799138957": "IRX6XTPI0006", "8384385859414435": "IRXYXTPI0026",
           "46342955726788357": "IRX6XSLC0006"}

regex = '<tr><td><a.*{index}">(.*)<\\/a>.*\\s\\n<td>(.*)<\\/td>\\s\\n<td>(.*)<\\/td>\\s\\n<td>.*>(.*)<.*<\\/td>\\s\\n<td>.*>(.*)<.*<\\/td>'


def _f(flt):
    chars_to_remove = [',', '(', ')']
    return float(''.join([c for c in flt if c not in chars_to_remove]))


# get_live_indices
def get_indices_live():
    data_live = requests.get(url=BASE_URL)
    result = []
    for indice in indices:
        res = re.findall(regex.format(index=indice), data_live.text)
        if len(res) > 0:
            res = res[0]
            result.append({
                "IndexChanges": _f(res[3]),
                "LastIndexValue": _f(res[2]),
                "PercentVariation": _f(res[4]),
                "SymbolTitle": res[0],
                "SymbolISIN": indices[indice]
            })

    return result
