from django.test import TestCase, RequestFactory
import unittest
import time


class LightStreamerTestCase(TestCase):

    fixtures = ['instrument']

    def test_online_plus_service(self):
        from .services.online_plus import LS_Class

        LS_Class()
        while True:
            time.sleep(10)
