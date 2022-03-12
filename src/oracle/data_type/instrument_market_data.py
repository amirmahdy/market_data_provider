import json
from oracle.cache.base import Cache

# data = {
#     "first_symbol_state": local_vals["first_symbol_state"],
#     "second_symbol_state": local_vals["second_symbol_state"],
#     "max_percent_change": local_vals["max_percent_change"],
#     "max_low_percent_change": local_vals["max_low_percent_change"],
#     "theoretical_openning_price": local_vals["theoretical_openning_price"],
#     "is_caution": local_vals["is_caution"],
#     "price_tick_size": local_vals["price_tick_size"],
#     "symbol_isin": isin,
#     "last_traded_price": vals["LastTradedPrice"],
#     "closing_price": vals["ClosingPrice"],
#     "high_allowed_price": vals["HighAllowedPrice"],
#     "low_allowed_price": vals["LowAllowedPrice"],
#     "price_var": vals["LastTradedPriceVarPercent"],
#     "price_change": vals["LastTradedPriceVar"],
#     "total_number_of_shares_traded": vals["TotalNumberOfSharesTraded"],
#     "company_name": local_vals["company_name"],
#     "en_company_name": local_vals["en_company_name"],
#     "closing_price_var": vals["ClosingPriceVarPercent"],
#     "closing_price_change": vals["ClosingPriceVar"],
#     "max_quantity_order": local_vals["max_quantity_order"],
#     "min_quantity_order": local_vals["min_quantity_order"],
#     "total_number_of_trades": vals["TotalNumberOfTrades"],
#     "total_trade_value": vals["TotalTradeValue"],
#     "low_price": vals["LowPrice"],
#     "high_price": vals["HighPrice"],
#     "trade_date": vals["TradeDate"],
#     "reference_price": vals["YesterdayPrice"],
#     "basis_volume": vals["BasisVolume"],
#     "percent_of_basis_volume": vals["BasisVolume"],
#     "symbol_fa": local_vals["symbol_fa"],
#     "symbol_en": local_vals["symbol_en"],
#     "first_traded_price": vals["FirstTradedPrice"],
#     "market_unit": "ETFStock",
#     "market_code": local_vals["market_code"],
#     "symbol_group_state": vals["SymbolStateId"],
#     "symbol_group_code": local_vals["symbol_group_code"],
#     "unit_count": local_vals["unit_count"],
#     "sector_code": local_vals["sector_code"],
#     "tomorrow_high_allowed_price": local_vals["tomorrow_high_allowed_price"],
#     "tomorrow_low_allowed_price": local_vals["tomorrow_low_allowed_price"],
#     "market_status": "ALLOWED",
# }
"""
A web service for getting market data.
"""


class Instrument_Maker_Data:

    def __call__(self, *args, **kwargs):
        ch = Cache()
        raw_res = ch.get(ref_group="market", ref_value=kwargs["isin"])
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
