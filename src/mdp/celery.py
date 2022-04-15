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
        'schedule': crontab(minute='*/1'),
        'args': ()
    },
    'tsetmc_askbid_yesterday_update': {
        'task': 'tsetmc_askbid_yesterday_update',
        'schedule': crontab(hour='6', minute='30'),
        'args': ()
    },
    'tsetmc_trade_yesterday_update': {
        'task': 'tsetmc_trade_yesterday_update',
        'schedule': crontab(hour='6', minute='0'),
        'args': ()
    },
    'tsetmc_trade_today_update': {
        'task': 'tsetmc_trade_today_update',
        'schedule': crontab(minute='*/1'),
        'args': ()
    }
}
