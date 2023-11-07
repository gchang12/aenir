#!/usr/bin/python3
"""
Tests the aenir._basemorph.BaseMorph class
"""

import json
import unittest
import logging
from unittest.mock import patch
import io

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

    def test_verify_clsrecon_file(self):
        """
        Displays names in clsrecon_dict that are not in their associated tables.
        """
        logging.info("BaseMorphTest.test_verify_clsrecon_file()")
        for clsrecon in self.sos_unit.clsrecon_list:
            self.sos_unit.verify_clsrecon_file(*clsrecon)

    def test_verify_maximum_stats(self):
        """
        Displays columns in 'characters/base-stats' that are missing from 'classes/maximum-stats'.
        """
        logging.info("BaseMorphTest.test_verify_maximum_stats()")
        self.sos_unit.verify_maximum_stats()

    def test_set_targetstats(self):
        """
        Tests the set_targetstats method.
        """
        logging.info("BaseMorphTest.test_set_targetstats()")
        # bases-to-growths
        ltable_url, lindex_val = "characters/base-stats", "Fir (HM)"
        rtable_url, to_col = "characters/growth-rates", "Name"
        self.sos_unit.set_targetstats(
                (ltable_url, lindex_val),
                (rtable_url, to_col),
                0,
                )
        self.assertIsInstance(self.sos_unit.target_stats, pd.Series)
        self.sos_unit.target_stats = None
        # bases-to-maxes
        rtable_url, to_col = "classes/maximum-stats", "Class"
        self.sos_unit.set_targetstats(
                (ltable_url, lindex_val),
                (rtable_url, to_col),
                0,
                )
        self.assertIsInstance(self.sos_unit.target_stats, pd.Series)
        self.sos_unit.target_stats = None
        # bases-to-promo
        rtable_url, to_col = "classes/promotion-gains", "Class"
        self.sos_unit.set_targetstats(
                (ltable_url, lindex_val),
                (rtable_url, to_col),
                0,
                )
        self.assertIsInstance(self.sos_unit.target_stats, pd.Series)
        new_cls = self.sos_unit.target_stats.at["Promotion"]
        self.sos_unit.target_stats = None
        # promo-to-maxes
        ltable_url, lindex_val = "classes/promotion-gains", new_cls
        rtable_url, to_col = "classes/maximum-stats", "Class"
        self.sos_unit.set_targetstats(
                (ltable_url, lindex_val),
                (rtable_url, to_col),
                0,
                )
        self.assertIsInstance(self.sos_unit.target_stats, pd.Series)
        self.sos_unit.target_stats = None
        # promo-to-promo
        rtable_url, to_col = "classes/promotion-gains", "Class"
        self.sos_unit.set_targetstats(
                (ltable_url, lindex_val),
                (rtable_url, to_col),
                0,
                )
        self.assertIsNone(self.sos_unit.target_stats)
        # bases-to-promo: fail
        ltable_url, lindex_val = "characters/base-stats", "Marcus"
        self.sos_unit.set_targetstats(
                (ltable_url, lindex_val),
                (rtable_url, to_col),
                0,
                )
        self.assertIsNone(self.sos_unit.target_stats)

    def test_get_character_list(self):
        """
        Tests the get_character_list method.

        Documents the errors that can be raised while callling this function.
        - FileNotFoundError: not home_dir.joinpath("characters__base_stats-JOIN-characters__growth_rates.json").exists()
        - json.decoder.JSONDecodeError: File is not in JSON form.
        """
        logging.info("BaseMorphTest.test_get_character_list()")
        # file does not exist
        with patch("pathlib.Path.joinpath") as mock_joinpath:
            mock_joinpath.return_value = ""
            with self.assertRaises(FileNotFoundError):
                self.sos_unit.get_character_list()
        # file is not in JSON format
        with patch("io.open") as mock_open:
            mock_open.return_value = io.StringIO()
            with self.assertRaises(json.decoder.JSONDecodeError):
                self.sos_unit.get_character_list()
        # main: list must contain no duplicates, and be a subset of 'characters/base-stats'['Name']
        chrlist = self.sos_unit.get_character_list()
        self.assertEqual(len(chrlist), len(set(chrlist)))
        bases_chrset = set()
        for table in self.sos_unit.url_to_tables['characters/base-stats']:
            bases_chrset.update(set(table.loc[:, "Name"]))
        self.assertTrue(set(chrlist).issubset(bases_chrset))
        trialmode_only = {
            "Narshen",
            "Gale",
            "Hector",
            "Brunya",
            "Eliwood",
            "Murdoch",
            "Zephiel",
            "Guinevere",
            }
        self.assertTrue(trialmode_only.isdisjoint(set(chrlist)))

if __name__ == '__main__':
    unittest.main(
        defaultTest="test_get_character_list",
        module=BaseMorphTest,
    )
