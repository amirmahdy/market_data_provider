from utils import AutoNameEnum
from enum import auto


class OrderSide(AutoNameEnum):
    BUY = auto()
    SELL = auto()


class QueueConditionOuput(AutoNameEnum):
    IS_BUY_QUEUE = auto()
    IS_SELL_QUEUE = auto()
    NEAR_BUY_QUEUE = auto()
    NEAR_SELL_QUEUE = auto()
    NOTHING = auto()


class OrderBalanceOutput(AutoNameEnum):
    BUY_HEAVIER = auto()
    SELL_HEAVIER = auto()
    NORMAL = auto()


class OrderDepthOutput(AutoNameEnum):
    HEAVY = auto()
    LIGHT = auto()
    NORMAL = auto()
    NONE = auto()


class RecentTradesOutput(AutoNameEnum):
    HIGH = auto()
    LOW = auto()
    NORMAL = auto()


class TriggerParameterName(AutoNameEnum):
    ROW = auto()    # Rolling Window
    LVT = auto()    # Low Volume Threashold
    HVT = auto()    # High Volume Threshold
    LDT = auto()    # High Depth Threshold
    HDT = auto()    # Low Depth Threshold
