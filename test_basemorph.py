#!/usr/bin/python3
"""
Tests the aenir._basemorph.BaseMorph class
"""

import unittest
import logging

from aenir._basemorph import BaseMorph

logging.basicConfig(level=logging.INFO)


class BaseMorphTest(unittest.TestCase):
    """
    Defines tests for name verification, and name look-up.
    """

    def setUp(self):
        """
        Initialize BaseMorph object; assume 'cleaned_stats.db' exists.
        """
        self.sos_unit = BaseMorph(6)
        self.sos_unit.tables_file = "cleaned_stats.db"
        for url in self.sos_unit.page_dict:
            self.sos_unit.load_tables(url)

    def test_verify_clsrecon_file(self):
        """
        Displays names of names in clsrecon_dict that are not in their associated tables.

        Note: logging.level must be set to logging.INFO for this method to work.
        """
        for clsrecon in self.sos_unit.clsrecon_list:
            self.sos_unit.verify_clsrecon_file(*clsrecon)

if __name__ == '__main__':
    unittest.main()
