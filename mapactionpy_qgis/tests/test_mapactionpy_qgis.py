from unittest import TestCase

import mapactionpy_qgis

class TestQgisRunner(TestCase):
    def test_alway_fail(self):
        self.assertTrue(false)
		
    def test_alway_pass(self):
        self.assertTrue(true)