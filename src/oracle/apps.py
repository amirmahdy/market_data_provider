from threading import Thread
from django.apps import AppConfig
import sys


class OracleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'oracle'

    def ready(self):
        from .services.online_plus import LS_Class
        from oracle.services.base import initial_setup
        from oracle.services.rayan import manage_rayan_webscoket

        if "worker" not in sys.argv:
            return True

        initial_setup()
        # engine_listener_thread = Thread(target=manage_rayan_webscoket, args=())
        # engine_listener_thread.start()
        LS_Class()
