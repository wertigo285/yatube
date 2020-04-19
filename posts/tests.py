from django.test import TestCase


class TestStringMethods2(TestCase):
    def test_length(self):
        self.assertEqual(len("yatube"), 6)
