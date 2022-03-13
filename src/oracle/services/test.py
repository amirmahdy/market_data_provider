import os, django
from django.test import TestCase


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mdp.settings")
django.setup()


class Test_Service(TestCase):

    def test_askbid(self):
        from oracle.services.tsetmc_askbid_history import get_askbid_history
        res = get_askbid_history('48010225447410247', '20220309')
        print(res)


tr = Test_Service()
tr.test_askbid()
