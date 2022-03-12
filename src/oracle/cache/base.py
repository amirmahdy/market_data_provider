import redis
import environ

env = environ.Env()


# def singleton(class_):
#     instances = {}
#
#     def getinstance(*args, **kwargs):
#         if "Instance" not in instances:
#             instances["Instance"] = class_(*args, **kwargs)
#         return instances["Instance"]
#
#     return getinstance
#
#
# @singleton
class Cache:
    def __init__(self):
        self.r = redis.Redis(host=env('REDIS'), port=env('REDISPORT'))

    def set(self, ref_group="", ref_value="", value=""):
        self.r.set(f"{ref_group}_{ref_value}", value)

    def get(self, ref_group="", ref_value="", tp=str):
        raw_res = self.r.get(f"{ref_group}_{ref_value}")
        return tp(raw_res.decode("utf-8")) if raw_res is not None else None
