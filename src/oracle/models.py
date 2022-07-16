import pickle
from django.db import models
from django.core.cache import cache


class InstrumentType(models.Model):
    code = models.IntegerField(default=0, unique=True, primary_key=True)
    name = models.CharField(max_length=64)
    desc = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name} - {self.code}"


class Instrument(models.Model):
    last_trade_date = models.IntegerField(default=0)
    tse_id = models.CharField(max_length=20)
    isin = models.CharField(max_length=12, primary_key=True)
    en_symbol = models.CharField(default="", max_length=20)
    en_symbol_18 = models.CharField(default="", max_length=25)
    en_code_5 = models.CharField(default="", max_length=10)
    name = models.CharField(max_length=128)
    symbol = models.CharField(max_length=64)
    fa_symbol_30 = models.CharField(default="", max_length=35)
    cisin = models.CharField(default="", max_length=18)
    nominal_val = models.FloatField(default=0, max_length=18)
    stock_qnt = models.FloatField(default=0, max_length=18)
    change_date = models.IntegerField(default=0)
    change_type = models.IntegerField(default=0)
    shit_type_AIO = models.CharField(default="", max_length=5)
    group_code = models.CharField(default="", max_length=5)
    initial_date = models.IntegerField(default=0)
    unit = models.IntegerField(default=0)
    market_code = models.CharField(default="", max_length=10)
    board_code = models.CharField(default="", max_length=10)
    ind_code = models.CharField(default="", max_length=10)
    sub_ind_code = models.CharField(default="", max_length=10)
    clear_delay = models.IntegerField(default=0)
    min_allowed_price = models.FloatField(default=0, max_length=10)
    max_allowed_price = models.FloatField(default=0, max_length=10)
    base_vol = models.CharField(default="", max_length=20)
    type = models.ForeignKey(InstrumentType, db_column="code", on_delete=models.CASCADE, default=0)
    tick_size = models.PositiveSmallIntegerField(default=1)
    trans_min_size = models.CharField(default="", max_length=20)
    flow = models.IntegerField(default=0)
    order_min_size = models.CharField(default="", max_length=20)
    order_max_size = models.CharField(default="", max_length=20)
    valid = models.BooleanField(default=False)
    market_status = models.CharField(max_length=20, default="A")
    rahavard_id = models.CharField(default="0", max_length=20)
    tick_needed = models.BooleanField(default=False)
    tadbir_id = models.CharField(default="", max_length=20)

    def __str__(self) -> str:
        return f"{self.isin}"

    def __repr__(self) -> str:
        return f"<{self.__str__()}>"

    @staticmethod
    def get_instruments():
        if cache.get("INSTRUMENT") is None:
            cache.set("INSTRUMENT", pickle.dumps(list(Instrument.objects.all())))
        return pickle.loads(cache.get("INSTRUMENT"))

    @staticmethod
    def get_instrument(ISIN):
        instruments = Instrument.get_instruments()
        return [instrument for instrument in instruments if instrument.isin == ISIN]


class TriggerParameter(models.Model):
    name = models.CharField(max_length=3, verbose_name='Parameter Name', primary_key=True)
    name_fa = models.CharField(max_length=128, verbose_name='Persian Name')
    description = models.CharField(max_length=1024, verbose_name='Description')
    value = models.CharField(max_length=32, verbose_name='Parameter Value')
    trigger_name = models.CharField(max_length=128, verbose_name='Trigger Name')

    def __str__(self):
        return self.name_fa
