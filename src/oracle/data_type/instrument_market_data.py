import json
from oracle.cache.base import Cache

"""
A web service for getting market data.
"""


class InstrumentData:
    @staticmethod
    def get(isin, ref_group):
        ch = Cache()
        raw_res = ch.get(ref_group=ref_group, ref_value=isin)
        return json.loads(raw_res) if raw_res is not None else None

    """
    Updating a portion of data from any source.
    """

    @staticmethod
    def update(isin, ref_group, value):
        ch = Cache()
        try:
            prev_val = ch.get(ref_group=ref_group, ref_value=isin)
            try:
                if prev_val is not None:
                    prev_val = json.loads(prev_val)
                    prev_val.update(value)
                    value = prev_val
            except Exception as e:
                pass

            value = json.dumps(value)
            ch.set(ref_group=ref_group, ref_value=isin, value=value)
            return True
        except Exception as e:
            print(e)
