from django.apps import AppConfig
import sys


class OracleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'oracle'

    def ready(self):
        from .services.online_plus import LS_Class
        # from oracle.services.base import initial_setup

        if "worker" not in sys.argv:
            return True

        # initial_setup()
        LS_Class()
