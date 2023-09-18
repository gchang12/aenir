#!/usr/bin/python3
"""
Defines the BaseMorphTest class for the aenir._basemorph.BaseMorph class.
"""

import unittest
from unittest.mock import patch

import pandas as pd

from aenir._basemorph import BaseMorph


class BaseMorphTest(unittest.TestCase):
    """
    Defines tests for the __init__ and set_target methods of BaseMorph.
    """

    def setUp(self):
        """
        Initialize BaseMorph instance, and set it to 'sos_unit'.
        """
        self.sos_unit = BaseMorph(6)

    def test__init__(self):
        """
        Tests that desired attributes are initialized, and that tables are loaded.
        """
        # check that the desired attributes are here
        self.assertEqual(self.sos_unit.current_clstype, "characters/base-stats")
        self.assertEqual(self.sos_unit.tables_file, "cleaned_stats.db")
        self.assertIn("target_stats", dir(self.sos_unit))
        # check that the tables have been loaded.
        self.assertNotEqual({}, self.sos_unit.url_to_tables)
        for tablelist in self.sos_unit.url_to_tables.values():
            self.assertIsInstance(tablelist, list)
            for table in tablelist:
                self.assertIsInstance(table, pd.DataFrame)
                self.assertFalse(table.empty)

    def test_set_targetstats__failures(self):
        """
        """
        # 1: current_clstype not in page_dict
        # 2: source_pkey not in clsrecon_dict
        # 3: source_pkey in clsrecon_dict
        # 4: target_cls is None
        # 5: target_cls is not None
        pass

if __name__ == '__main__':
    unittest.main()
