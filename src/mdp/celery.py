from __future__ import absolute_import
import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mdp.settings")

app = Celery("mdp")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'tsetmc_market_data_update': {
        'task': 'tsetmc_market_data_update',
        'schedule': crontab(hour="*,8-13", minute='*/1'),
        'args': ()
    },
    'tsetmc_askbid_yesterday_update': {
        'task': 'tsetmc_askbid_yesterday_update',
        'schedule': crontab(hour='6', minute='30'),
        'args': (1,)
    },
    'tsetmc_trade_kline': {
        'task': 'tsetmc_trade_kline',
        'schedule': crontab(hour='6', minute='15'),
        'args': (1,)
    },
    'tsetmc_trade_yesterday_update': {
        'task': 'tsetmc_trade_yesterday_update',
        'schedule': crontab(hour='6', minute='0'),
        'args': (1,)
    },
    'trade_tick_data': {
        'task': 'trade_tick_data',
        'schedule': crontab(hour='5', minute='45'),
        'args': ()
    },
    'tsetmc_trade_today_update': {
        'task': 'tsetmc_trade_today_update',
        'schedule': crontab(minute='*/1'),
        'args': ()
    },
    'check_queue_condition': {
        'task': 'check_queue_condition',
        'schedule': crontab(minute='*/1'),
        'args': ()
    },
    'check_order_balance': {
        'task': 'check_order_balance',
        'schedule': crontab(minute='*/1'),
        'args': ()
    },
    'check_order_depth': {
        'task': 'check_order_depth',
        'schedule': crontab(minute='*/1'),
        'args': ()
    },
    'check_recent_trades': {
        'task': 'check_recent_trades',
        'schedule': crontab(minute='*/1'),
        'args': ()
    },
    'online_plus_socket_renew': {
        'task': 'online_plus_socket_renew',
        'schedule': crontab(hour='6', minute='0'),
        'args': ()
    },
    'instrument_update': {
        'task': 'instrument_update',
        'schedule': crontab(hour='6', minute='10'),
        'args': ()
    },

}
