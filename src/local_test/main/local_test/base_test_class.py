from unittest import TestCase

from pyfakefs.fake_filesystem_unittest import TestCase as PyfakefsTestCase


class BaseTestClass(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None


class BasePyfakefsTestClass(PyfakefsTestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
