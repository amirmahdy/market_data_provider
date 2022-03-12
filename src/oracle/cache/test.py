from django.test import TestCase


class Test_Cache(TestCase):
    def setUp(self) -> None:
        from oracle.cache.base import Cache
        self.cache = Cache()

    def test_input(self):
        self.cache.set("inst_data", "IRO1BANK0001", 1000)
        self.assertEqual(self.cache.get("inst_data", "IRO1BANK0001", int), 1000)


if __name__ == "__main__":
    tc = Test_Cache()
    tc.setUp()
    tc.test_input()
