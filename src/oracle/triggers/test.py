import os, django
from django.test import TestCase

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mdp.settings")
django.setup()


class Test_Service(TestCase):

    def test_broadcast_instrument_queue_status(self):
        from oracle.triggers.queue_condition import broadcast_instrument_queue_status
        broadcast_instrument_queue_status("IRO1BANK0001")


tr = Test_Service()
tr.test_broadcast_instrument_queue_status()
