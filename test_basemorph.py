#!/usr/bin/python3
"""
Tests the aenir._basemorph.BaseMorph class
"""

import unittest
import logging

import pandas as pd

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
        Displays names in clsrecon_dict that are not in their associated tables.
        """
        logging.info("BaseMorphTest.test_verify_clsrecon_file(self)")
        for clsrecon in self.sos_unit.clsrecon_list:
            self.sos_unit.verify_clsrecon_file(*clsrecon)

    def test_verify_maximum_stats(self):
        """
        Displays columns in 'characters/base-stats' that are missing from 'classes/maximum-stats'.
        """
        logging.info("BaseMorphTest.test_verify_maximum_stats(self)")
        self.sos_unit.verify_maximum_stats()

    def test_set_targetstats(self):
        """
        Tests the set_targetstats method.
        """
        logging.info("BaseMorphTest.test_set_targetstats(self)")
        # bases-to-growths
        ltable_url, lpval = "characters/base-stats", "Fir (HM)"
        rtable_url, to_col = "characters/growth-rates", "Name"
        self.sos_unit.set_targetstats(
                (ltable_url, lpval),
                (rtable_url, to_col),
                0,
                )
        self.assertIsInstance(self.sos_unit.target_stats, pd.Series)
        self.sos_unit.target_stats = None
        # bases-to-maxes
        rtable_url, to_col = "classes/maximum-stats", "Class"
        self.sos_unit.set_targetstats(
                (ltable_url, lpval),
                (rtable_url, to_col),
                0,
                )
        self.assertIsInstance(self.sos_unit.target_stats, pd.Series)
        self.sos_unit.target_stats = None
        # bases-to-promo
        rtable_url, to_col = "classes/promotion-gains", "Class"
        self.sos_unit.set_targetstats(
                (ltable_url, lpval),
                (rtable_url, to_col),
                0,
                )
        self.assertIsInstance(self.sos_unit.target_stats, pd.Series)
        new_cls = self.sos_unit.target_stats.at["Promotion"]
        self.sos_unit.target_stats = None
        # promo-to-maxes
        ltable_url, lpval = "classes/promotion-gains", new_cls
        rtable_url, to_col = "classes/maximum-stats", "Class"
        self.sos_unit.set_targetstats(
                (ltable_url, lpval),
                (rtable_url, to_col),
                0,
                )
        self.assertIsInstance(self.sos_unit.target_stats, pd.Series)
        self.sos_unit.target_stats = None
        # promo-to-promo
        rtable_url, to_col = "classes/promotion-gains", "Class"
        self.sos_unit.set_targetstats(
                (ltable_url, lpval),
                (rtable_url, to_col),
                0,
                )
        self.assertIsNone(self.sos_unit.target_stats)
        # bases-to-promo: fail
        ltable_url, lpval = "characters/base-stats", "Marcus"
        self.sos_unit.set_targetstats(
                (ltable_url, lpval),
                (rtable_url, to_col),
                0,
                )
        self.assertIsNone(self.sos_unit.target_stats)

if __name__ == '__main__':
    unittest.main()
