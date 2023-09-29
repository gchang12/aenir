#!/usr/bin/python3
"""
"""

import unittest
import logging
import json

import pandas as pd


from aenir.morph import Morph

logging.basicConfig(level=logging.WARNING)

class Morph6Test(unittest.TestCase):

    def setUp(self):
        self.roy = Morph(6, "Roy", datadir_root="data")
        # create a copy of Roy's stats, level-up, cap, and assert that the bonuses have been applied
        # create a copy of everyone's stats
        # put them through the whole: level-up 'til max, try to promote: level-up 'til max

    def test_level_up(self):
        current_stat_copy = self.roy.current_stats.copy()
        growths = self.roy.url_to_tables['characters/growth-rates'][0].set_index("Name").loc["Roy", :]
        target_lv = 20
        self.roy.level_up(target_lv)
        self.assertTrue(all((current_stat_copy + (growths / 100) * 19) == self.roy.current_stats))
        self.assertEqual(self.roy.current_lv, target_lv)

    def test_cap_stats(self):
        for statname in self.roy.current_stats.index:
            self.roy.current_stats.at[statname] = 99
        self.roy.current_stats.at["HP"] = 5
        self.roy.cap_stats()
        maxes = self.roy.url_to_tables["classes/maximum-stats"][0].set_index("Class").loc["Non-promoted", :]
        roy_hp = self.roy.current_stats.pop("HP")
        maxes.pop("HP")
        self.assertTrue(all(self.roy.current_stats == maxes))
        self.assertEqual(roy_hp, 5)

    def test_promote(self):
        promo = self.roy.url_to_tables['classes/promotion-gains'][0].set_index("Class").loc["Lord", :]
        promo.pop("Promotion")
        promo = promo.reindex(self.roy.current_stats.index, fill_value=0.0)
        current_stat_copy = self.roy.current_stats.copy()
        self.roy.promote()
        self.assertTrue(all(current_stat_copy + promo == self.roy.current_stats))
        self.assertEqual(self.roy.current_lv, 1)
        self.assertListEqual(self.roy.history, [("Lord", 1)])
        self.assertEqual(self.roy.current_cls, "Master Lord")

    def test_roy(self):
        # https://serenesforest.net/binding-blade/characters/average-stats/normal-mode/roy/
        # 1: max stats, and compare with source
        self.roy.level_up(target_lv=20)
        self.roy.cap_stats()
        lv20_roy = {
                "HP": 33.2,
                "Pow": 12.6,
                "Skl": 14.5,
                "Spd": 14.6,
                "Lck": 18.4,
                "Def": 9.75,
                "Res": 5.7,
                }
        self.assertTrue(all(abs(pd.Series(lv20_roy) - self.roy.current_stats) < 0.01))
        # 2: promote, and compare
        self.roy.promote()
        self.roy.cap_stats()
        # 3: max stats, and compare
        self.roy.level_up(target_lv=20)
        self.roy.cap_stats()
        maxed_roy = {
                "HP": 52.4,
                "Pow": 22.2,
                "Skl": 25,
                "Spd": 24.2,
                "Lck": 29.8,
                "Def": 16.5,
                "Res": 16.4,
                }
        self.assertTrue(all(abs(pd.Series(maxed_roy) - self.roy.current_stats) < 0.01))

    def test_all_units(self):
        ltable = "characters__base_stats"
        rtable = "classes__promotion_gains"
        with open(
                str(self.roy.home_dir.joinpath(f"{ltable}-JOIN-{rtable}.json")),
                encoding='utf-8') as rfile:
            promocls_dict = json.load(rfile)
        bases = self.roy.url_to_tables['characters/base-stats'][0].set_index("Name")
        bases.pop("Class")
        bases.pop("Lv")
        for unitname in self.roy.url_to_tables['characters/growth-rates'][0]["Name"]:
            unit = Morph(6, unitname)
            promocls = promocls_dict[unitname]
            if promocls is None:
                with self.assertRaises(ValueError):
                    unit.promote()
                try:
                    unit.level_up(target_lv=20)
                    unit.cap_stats()
                except ValueError:
                    logging.info(f"{unitname} is already maxed.")
                    continue
            else:
                unit.level_up(target_lv=20)
                unit.cap_stats()
                unit.promote()
                unit.cap_stats()
                unit.level_up(20)
                unit.cap_stats()
            self.assertTrue(any(unit.current_stats > bases.loc[unitname, :]))

    def test_level_up__failures(self):
        # 1: target_lv > maxlv
        with self.assertRaises(ValueError):
            self.roy.level_up(99)
        # 2: target_lv < current_lv := 1
        with self.assertRaises(ValueError):
            self.roy.level_up(0)

    def test_promote__failures(self):
        # 1: promo-lv not high enough
        with self.assertRaises(ValueError):
            self.roy.current_lv = 0
            self.roy.promote()
        # 2: already promoted
        self.roy.current_lv = 2
        self.roy.promote()
        history_copy = self.roy.history.copy()
        stats_copy = self.roy.current_stats.copy()
        cls_copy = self.roy.current_cls
        lv_copy = self.roy.current_lv
        with self.assertRaises(ValueError):
            self.roy.promote()
        self.assertListEqual(history_copy, self.roy.history)
        self.assertTrue(all(stats_copy == self.roy.current_stats))
        self.assertEqual(cls_copy, self.roy.current_cls)
        self.assertEqual(lv_copy, self.roy.current_lv)

if __name__ == '__main__':
    unittest.main()
