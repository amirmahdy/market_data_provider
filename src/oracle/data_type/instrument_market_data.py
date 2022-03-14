import json
from oracle.cache.base import Cache

"""
A web service for getting market data.
"""


class Instrument_Maker_Data:
    @staticmethod
    def get(isin):
        ch = Cache()
        raw_res = ch.get(ref_group="market", ref_value=isin)
        return json.loads(raw_res) if raw_res is not None else None

    """
    Updating a portion of data from any source.
    """

    @staticmethod
    def update(isin, value):
        ch = Cache()
        try:
            prev_val = ch.get(ref_group="market", ref_value=isin)
            if prev_val is not None:
                prev_val = json.loads(prev_val)
                value.update(prev_val)

            value = json.dumps(value)
            ch.set(ref_group="market", ref_value=isin, value=value)
            return True
        except Exception as e:
            print(e)
