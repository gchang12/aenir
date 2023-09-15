#!/usr/bin/python3
"""
"""

import unittest

from aenir._base import SerenesBase


class BaseTest(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    def test__init__KeyError(self):
        """
        """
        # key is invalid by virtue of not being registered
        self.assertNotIn(None , SerenesBase._NUM_TO_NAME)
        # main: init fails because argument is not a valid key
        with self.assertRaises(KeyError):
            base = SerenesBase(None)

    def test__init__(self):
        """
        """
        # key is valid because it has been registered
        self.assertIn(6 , SerenesBase._NUM_TO_NAME)
        # main
        base = SerenesBase(6)
        # assert that these are all properties
        with self.assertRaises(AttributeError):
            base.game_num = None
        with self.assertRaises(AttributeError):
            base.game_name = None
        with self.assertRaises(AttributeError):
            base.URL_ROOT = None
        with self.assertRaises(AttributeError):
            base.NUM_TO_NAME = None

if __name__ == '__main__':
    unittest.main()
