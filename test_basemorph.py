#!/usr/bin/python3
"""
"""

import unittest
import pandas as pd

from aenir._basemorph import BaseMorph


class BaseMorphTest(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        self.roy = BaseMorph(6, "Roy")

    def tearDown(self):
        """
        """
        pass


if __name__ == '__main__':
    unittest.main()
