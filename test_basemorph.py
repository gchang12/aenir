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

    def test_set_targetstats1(self):
        """
        Tests the function from top to bottom, and documents all failures and branches.
        """
        target_urlpath = "classes/maximum-stats"
        target_pkey = ["Class"]
        # 1: current_clstype not in page_dict
        self.sos_unit.current_clstype = None
        with self.assertRaises(KeyError):
            self.sos_unit.set_targetstats(target_urlpath, "Roy", target_pkey, 0)
            self.assertIsNone(self.sos_unit.target_stats)
        self.sos_unit.current_clstype = "characters/base-stats"
        # 2: target_cls not in stat_table
        with self.assertRaises(KeyError):
            self.sos_unit.current_cls = ""
            self.sos_unit.set_targetstats(target_urlpath, "", target_pkey, 0)
            self.assertIsNone(self.sos_unit.target_stats)
        # 3: target_pkey not a column
        with self.assertRaises(KeyError):
            self.sos_unit.set_targetstats(target_urlpath, "Roy", "", 0)
            self.assertIsNone(self.sos_unit.target_stats)
        # 4: home_pval in clsrecon_dict
        #Every character is in the classes/maximum-stats table
        self.sos_unit.set_targetstats(target_urlpath, "Roy", target_pkey, 0)
        self.assertIsInstance(self.sos_unit.target_stats, pd.Series)
        self.sos_unit.target_stats = None
        # 5: target_cls is None
        #Marcus: Promoted, and so would have no target class
        self.sos_unit.set_targetstats("classes/promotion-gains", "Marcus", target_pkey, 0)
        self.assertIsNone(self.sos_unit.target_stats)
        # 6: home_pval not found
        #Roy: Lord->Master Lord is not in clsrecon_dict
        self.sos_unit.current_cls = "Lord"
        self.sos_unit.set_targetstats("classes/promotion-gains", "Roy", "Class", 0)
        self.assertIsInstance(self.sos_unit.target_stats, pd.Series)

    def test_set_targetstats2(self):
        """
        Tests for all cases that will be encountered during program usage.

        # bases-to-maxes
        # promo-to-maxes
        # bases-to-promo
        # bases-to-promo: fail
        """
        # bases-to-maxes
        target_urlpath = "classes/maximum-stats"
        target_pkey = ["Class"]
        self.sos_unit.set_targetstats(target_urlpath, "Marcus", target_pkey, 0)
        self.assertIsInstance(self.sos_unit.target_stats, pd.Series)
        # promo-to-maxes
        self.sos_unit.current_clstype = "classes/promotion-gains"
        self.sos_unit.current_cls = "Master Lord"
        self.sos_unit.set_targetstats(target_urlpath, "Roy", target_pkey, 0)
        self.assertIsInstance(self.sos_unit.target_stats, pd.Series)
        # bases-to-promo
        self.sos_unit.current_clstype = "characters/base-stats"
        self.sos_unit.current_cls = "Cavalier"
        self.sos_unit.set_targetstats("classes/promotion-gains", "Allen", target_pkey, 0)
        self.assertIsInstance(self.sos_unit.target_stats, pd.Series)
        # bases-to-promo: fail
        self.sos_unit.current_clstype = "characters/base-stats"
        self.sos_unit.current_cls = "Hero"
        self.sos_unit.set_targetstats("classes/promotion-gains", "Echidna", target_pkey, 0)
        self.assertIsNone(self.sos_unit.target_stats)

    @patch("io.open")
    def test_set_targetstats__filenotfound(self, mock_open):
        """
        Tests that the state of the BaseMorph remains the same if the file is not found.

        This will be useful when referencing the static filetree on the web.
        """
        # 6: file not found
        target_urlpath = "classes/maximum-stats"
        target_pkey = ["Class"]
        mock_open.side_effect = FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            self.sos_unit.set_targetstats(target_urlpath, "Roy", target_pkey, 0)
            self.assertIsNone(self.sos_unit.targetstats)

if __name__ == '__main__':
    unittest.main()
