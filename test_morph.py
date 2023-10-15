#!/usr/bin/python3
"""
Tests the aenir.morph.Morph class methods.
"""

import unittest
import logging
import json

import pandas as pd


from aenir.morph import Morph, Morph4, Morph5, Morph7

logging.basicConfig(level=logging.INFO)

class Morph6Test(unittest.TestCase):
    """
    Defines tests for leveling up, promoting, and capping stats.
    """

    def setUp(self):
        """
        Creates a Morph object, with the option specified for full coverage.
        """
        self.roy = Morph(6, "Roy", datadir_root="data")
        # create a copy of Roy's stats, level-up, cap, and assert that the bonuses have been applied
        # create a copy of everyone's stats
        # put them through the whole: level-up 'til max, try to promote: level-up 'til max

    def test_level_up(self):
        """
        Tests that the current_lv and current_stats have been incremented.

        Assert:
        - current_lv = 20
        - current_stats = base_stats + (growths/100) * 19
        """
        current_stat_copy = self.roy.current_stats.copy()
        growths = self.roy.url_to_tables['characters/growth-rates'][0].set_index("Name").loc["Roy", :]
        target_lv = 20
        self.roy.level_up(target_lv)
        self.assertTrue(all((current_stat_copy + (growths / 100) * 19) == self.roy.current_stats))
        self.assertEqual(self.roy.current_lv, target_lv)

    def test_cap_stats(self):
        """
        Tests that the stats are capped in accordance with the current class.

        Sets the current stats to 99, except for HP, which is 5.
        Assert:
        - all stats are equal to max, except for HP, which is 5.
        """
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
        """
        Tests that the promotion has been applied properly.

        Assert:
        - current_stats = current_stats + promo_bonus
        - current_lv = 1
        - history = (Lord, 1)
        - current_cls = Master Lord
        - current_clstype = 'classes/promotion-gains'
        """
        promo = self.roy.url_to_tables['classes/promotion-gains'][0].set_index("Class").loc["Lord", :]
        promo.pop("Promotion")
        promo = promo.reindex(self.roy.current_stats.index, fill_value=0.0)
        current_stat_copy = self.roy.current_stats.copy()
        self.roy.promote()
        self.assertTrue(all(current_stat_copy + promo == self.roy.current_stats))
        self.assertEqual(self.roy.current_lv, 1)
        self.assertListEqual(self.roy.history, [("Lord", 1)])
        self.assertEqual(self.roy.current_cls, "Master Lord")
        self.assertEqual(self.roy.current_clstype, "classes/promotion-gains")

    def test_roy(self):
        """
        In-depth test of leveling up and promoting Roy.

        Tests for stat equality at the following checkpoints:
        - Lv20 Lord
        - Lv20 Master Lord
        """
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
        """
        Performs a shallow test: each unit is put through a maxing journey.

        Assert: final > bases
        """
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
        """
        Verifies that the ValueError is raised in specific situations.
        """
        # 1: target_lv > maxlv
        with self.assertRaises(ValueError):
            self.roy.level_up(99)
        # 2: target_lv < current_lv := 1
        with self.assertRaises(ValueError):
            self.roy.level_up(0)

    def test_promote__failures(self):
        """
        Verifies that the ValueError is raised in specific situations.
        """
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
        # verify that old data is retained.
        self.assertListEqual(history_copy, self.roy.history)
        self.assertTrue(all(stats_copy == self.roy.current_stats))
        self.assertEqual(cls_copy, self.roy.current_cls)
        self.assertEqual(lv_copy, self.roy.current_lv)

    def test_is_maxed(self):
        """
        Verifies that the pd.Series lists which stats are maxed (=True).

        Case: Luck maxes out at 30
        """
        mock_maxed = pd.Series(index=self.roy.current_stats.index, data=[False for stat in self.roy.current_stats])
        mock_maxed['Lck'] = True
        self.roy.current_stats['Lck'] = 30
        self.assertTrue(all(self.roy.is_maxed() == mock_maxed))

    def test__lt__(self):
        """
        Verifies that the pd.DataFrame returned summarizes the differences between Morph objects.
        """
        # max out Roy first
        marcus = Morph(6, "Marcus")
        comparison_df = self.roy < marcus
        c_roy = comparison_df['Roy']
        self.assertEqual(c_roy.pop("Class"), self.roy.current_cls)
        self.assertEqual(c_roy.pop("Lv"), self.roy.current_lv)
        #self.assertListEqual(list(c_roy.pop("PrevClassLv")), self.roy.history)
        self.assertTrue(all(c_roy == self.roy.current_stats))
        c_marcus = comparison_df['Marcus']
        self.assertEqual(c_marcus.pop("Class"), marcus.current_cls)
        self.assertEqual(c_marcus.pop("Lv"), marcus.current_lv)
        #self.assertListEqual(list(c_marcus.pop("PrevClassLv")), marcus.history)
        self.assertTrue(all(c_marcus == marcus.current_stats))

class Morph4Test(unittest.TestCase):
    def setUp(self):
        # create Morph of FE4 kid
        self.identifier = ("Lakche", "Lex")
        self.lakche = Morph4(*self.identifier)
        # create copy of bases for easy reference
        self.bases = self.lakche.url_to_tables["characters/base-stats"][1].set_index(["Name", "Father"]).loc[self.identifier, :].copy()
        self.bases.pop("Class")
        self.bases.pop("Lv")

    def test_level_up(self):
        # test modified level-up method
        growths = self.lakche.url_to_tables["characters/growth-rates"][1].set_index(["Name", "Father"]).loc[self.identifier, :]
        expected = (1.0 * self.bases) + growths * (20 - self.lakche.current_lv) / 100
        self.lakche.level_up(20)
        self.assertTrue(all(abs(self.lakche.current_stats - expected) < 0.01))

    def test_promote(self):
        # test FE4 promotion
        current_lv = 20
        self.lakche.current_lv = current_lv
        self.lakche.promote()
        self.assertEqual(self.lakche.current_cls, "Swordmaster")
        self.assertEqual(self.lakche.current_lv, current_lv)
        temp_promo = self.lakche.url_to_tables['classes/promotion-gains'][0].set_index(["Class", "Promotion"]).loc[("Swordfighter", "Swordmaster"), :].reindex(self.bases.index, fill_value=0.0) * 1.0
        self.assertTrue(all(abs(self.lakche.current_stats - self.bases - temp_promo) < 0.01))


class Morph5Test(unittest.TestCase):
    def setUp(self):
        self.lara = Morph5("Lara")
        self.bases = self.lara.current_stats.copy()
        # initialize promo bonuses for all scenarios
        promo_table = self.lara.url_to_tables["classes/promotion-gains"][0].set_index(["Class", "Promotion"])
        self.dancer__to__thief_fighter = promo_table.loc[("Dancer", "Thief Fighter"), :].reindex(self.bases.index, fill_value=0.0)
        self.thief__to__dancer = promo_table.loc[("Thief", "Dancer"), :].reindex(self.bases.index, fill_value=0.0)
        self.thief_fighter__to__dancer = promo_table.loc[("Thief Fighter", "Dancer"), :].reindex(self.bases.index, fill_value=0.0)
        self.thief__to__thief_fighter = promo_table.loc[("Thief", "Thief Fighter"), :].reindex(self.bases.index, fill_value=0.0)

    def test_promote1(self):
        # Thief -> Thief Fighter -> Dancer -> Thief Fighter
        self.lara.current_lv = 10
        with self.assertRaises(KeyError):
            # should complain about lack of promo_cls attribute
            self.lara.promote()
        self.lara.promo_cls = "Thief Fighter"
        # Thief -> Thief Fighter
        self.lara.promote()
        running_bonus = self.thief__to__thief_fighter.copy()
        # test for equality: cls, lv, stats
        self.assertTrue(all(abs(self.lara.current_stats - self.bases - running_bonus) < 0.01))
        self.assertEqual(self.lara.current_cls, "Thief Fighter")
        self.assertEqual(self.lara.current_lv, 1)
        # should raise a ValueError because "Lara" is not Lara
        self.lara.unit_name = "Lifis"
        with self.assertRaises(ValueError):
            self.lara.promote()
        # restore name
        self.lara.unit_name = "Lara"
        # Thief Fighter -> Dancer
        running_bonus += self.thief_fighter__to__dancer
        self.lara.promo_cls = "Dancer"
        self.lara.promote()
        self.assertTrue(all(abs(self.lara.current_stats - self.bases - running_bonus) < 0.01))
        self.assertEqual(self.lara.current_cls, "Dancer")
        self.assertEqual(self.lara.current_lv, 1)
        # Dancer -> Thief Fighter
        #self.promo_cls = "Thief Fighter"
        self.lara.current_lv = 10
        self.lara.promote()
        running_bonus += self.dancer__to__thief_fighter
        self.assertTrue(all(abs(self.lara.current_stats - self.bases - running_bonus) < 0.01))
        self.assertEqual(self.lara.current_cls, "Thief Fighter")
        self.assertEqual(self.lara.current_lv, 1)
        # Thief Fighter -> Dancer
        with self.assertRaises(ValueError):
            self.lara.promote()

    def test_promote2(self):
        # Thief -> Dancer -> Thief Fighter
        self.lara.promo_cls = "Dancer"
        self.assertEqual(self.lara.current_lv, 1)
        self.lara.promote()
        running_bonus = self.thief__to__dancer.copy()
        # Thief -> Dancer
        self.assertTrue(all(abs(self.lara.current_stats - self.bases - running_bonus) < 0.01))
        self.assertEqual(self.lara.current_cls, "Dancer")
        self.assertEqual(self.lara.current_lv, 1)
        running_bonus += self.dancer__to__thief_fighter
        # Thief Fighter -> Dancer
        self.lara.current_lv = 10
        self.lara.promote()
        self.assertTrue(all(abs(self.lara.current_stats - self.bases - running_bonus) < 0.01))
        self.assertEqual(self.lara.current_cls, "Thief Fighter")
        self.assertEqual(self.lara.current_lv, 1)
        self.lara.promo_cls = "Dancer"
        # Dancer -> Thief Fighter
        with self.assertRaises(ValueError):
            self.lara.promote()

class Morph7Test(unittest.TestCase):
    def setUp(self):
        # initialize both versions of Wallace
        self.wallace0 = Morph7("Wallace", lyn_mode=True)
        self.wallace1 = Morph7("Wallace", lyn_mode=False)
        self.growths = self.wallace0.url_to_tables["characters/growth-rates"][0].set_index("Name").loc["Wallace", :]

    def test_tutorial_wallace(self):
        # max out level -> promote -> cap stats
        bases = self.wallace0.current_stats.copy()
        # test level-up
        self.wallace0.level_up(20)
        running_total = self.growths.copy() * 7.0 / 100
        self.assertTrue(all(abs(self.wallace0.current_stats - bases - running_total)))
        # test promotion
        promo_table = self.wallace0.url_to_tables["classes/promotion-gains"][0].set_index(["Class", "Promotion"])
        running_total += promo_table.loc[(self.wallace0.current_cls, "General (M)"), :].reindex(bases.index, fill_value=0.0)
        self.wallace0.promote()
        # assert that Wallace cannot promote again
        with self.assertRaises(ValueError):
            self.wallace0.promote()
        # - test that stats match
        self.assertTrue(all(abs(self.wallace0.current_stats - bases - running_total)))
        self.wallace0.cap_stats()
        # test that the target stats that referenced the maxes has name = 'General (M)'
        self.assertEqual(self.wallace0.target_stats.name, "General (M)")
        # test that lv, cls match expected
        self.assertEqual(self.wallace0.current_lv, 1)
        self.assertEqual(self.wallace0.current_cls, "General (M)")
        #running_total += self.growths * 19.0 / 100
        #self.wallace0.level_up(20)
        #self.assertTrue(all(abs(self.wallace0.current_stats - bases - running_total)))

    def test_main_wallace(self):
        # fail: promote
        self.assertEqual("classes/promotion-gains", self.wallace1.current_clstype)
        with self.assertRaises(ValueError):
            self.wallace1.promote()
        # test: level-up
        bases = self.wallace1.current_stats.copy()
        self.wallace1.level_up(20)
        running_total = self.growths.copy() * 19.0 / 100
        self.assertTrue(all(abs(self.wallace1.current_stats - bases - running_total) < 0.01))

if __name__ == '__main__':
    unittest.main(
        defaultTest=["test"],
        module=Morph7Test,
    )
