import json
from datetime import datetime

from oracle.cache.base import Cache


class HeartBeat:
    @staticmethod
    def get(source, ref_value):
        ch = Cache()
        raw_res = ch.get(ref_group="heart_beat", ref_value=source + "_" + ref_value)
        return json.loads(raw_res) if raw_res is not None else None

    @staticmethod
    def update(source, ref_value):
        ch = Cache()
        date = datetime.now()
        value = {"time": str(date)}
        try:
            value = json.dumps(value)
            ch.set(ref_group="heart_beat", ref_value=source + "_" + ref_value, value=value)
            return True
        except Exception as e:
            print(e)
