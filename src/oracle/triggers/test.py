import os, django
from django.test import TestCase

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mdp.settings")
django.setup()


class Test_Service(TestCase):

    def test_check_instrument_queue_status(self):
        from oracle.triggers.queue_condition import check_instrument_queue_status
        check_instrument_queue_status("IRO1BANK0001")


tr = Test_Service()
tr.test_check_instrument_queue_status()
