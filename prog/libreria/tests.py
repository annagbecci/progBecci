from django.test import TestCase


class SimpleTest(TestCase):
    def test_prova(self):
        self.assertEqual(2, (1+1))
