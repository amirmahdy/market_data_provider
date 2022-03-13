from dataclasses import dataclass


@dataclass
class MarketDataType:
    first_symbol_state: int
    second_symbol_state: int
    max_percent_change: int
    max_low_percent_change: int
    theoretical_openning_price: int
    is_caution: bool
    price_tick_size: int
    symbol_isin: str
    last_traded_price: int
    closing_price: int
    high_allowed_price: int
    low_allowed_price: int
    price_var: float
    price_change: float
    total_number_of_shares_traded: int
    company_name: str
    en_company_name: str
    closing_price_var: float
    closing_price_change: float
    max_quantity_order: int
    min_quantity_order: int
    total_number_of_trades: int
    total_trade_value: int
    low_price: int
    high_price: int
    trade_date: str
    reference_price: int
    basis_volume: int
    percent_of_basis_volume: float
    symbol_fa: str
    symbol_en: str
    first_traded_price: int
    market_unit: str
    market_code: str
    symbol_group_state: int
    symbol_group_code: str
    unit_count: int
    sector_code: str
    tomorrow_high_allowed_price: int
    tomorrow_low_allowed_price: int
    market_status: str
