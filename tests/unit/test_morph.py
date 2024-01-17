#!/usr/bin/python3
"""
Tests the aenir.morph.Morph class methods.
"""

from unittest.mock import patch
import unittest
import logging
import json

import pandas as pd


from aenir._basemorph import BaseMorph
from aenir.morph import Morph, Morph4, Morph5, Morph6, Morph7, Morph8, Morph9

logging.basicConfig(level=logging.CRITICAL)

class Morph6Test(unittest.TestCase):
    """
    Defines tests for leveling up, promoting, and capping stats.
    """

    def setUp(self):
        """
        Creates a Morph object, with the option specified for full coverage.
        """
        self.roy = Morph(6, "Roy", datadir_root="data")
        self.assertFalse(any(self.roy.current_stats.isnull()))
        # create a copy of Roy's stats, level-up, cap, and assert that the bonuses have been applied
        # create a copy of everyone's stats
        # put them through the whole: level-up 'til max, try to promote: level-up 'til max

    def test__init__unit_dne(self):
        """
        Tests that a KeyError is raised if the unit is not found.
        """
        with self.assertRaises(KeyError):
            marth = Morph(6, "Marth")

    @patch("copy.deepcopy")
    def test_copy(self, mock_copy):
        """
        Tests that the copy.deepcopy method was invoked in instance method.
        """
        logging.info("Morph6Test.test_copy()")
        logging.warning("Asserting that Morph.copy method returns copy.deepcopy(self).")
        roy_copy = self.roy.copy()
        self.assertIs(roy_copy, mock_copy.return_value)
        logging.warning("Morph.copy method returns copy.deepcopy(self).")
        logging.warning("Asserting that target_stats is None.")
        self.assertIsNone(self.roy.target_stats)
        logging.warning("target_stats is None.")
        logging.warning("Asserting that copy.deepcopy was called with instance as argument.")
        mock_copy.assert_called_once_with(self.roy)
        logging.warning("copy.deepcopy was called with instance as argument.")

    def test_copy2(self):
        """
        Tests that the copy method returns a Morph that can be compared to the original.
        """
        logging.info("Morph6Test.test_copy2()")
        roy_copy = self.roy.copy()
        comparison = roy_copy < self.roy
        self.assertIsInstance(comparison, pd.DataFrame)
        print(comparison)
        self.assertEqual(self.roy.current_stats.name, self.roy.unit_name)
        self.assertEqual(roy_copy.current_stats.name, roy_copy.unit_name)
        self.assertIsNot(self.roy.current_stats, roy_copy.current_stats)
        self.assertTrue(all(self.roy.current_stats == roy_copy.current_stats))

    def test__eq__(self):
        """
        Tests that equality as defined fails and succeeds as expected.
        """
        logging.info("Morph6Test.test__eq__()")
        marcus = Morph(6, "Marcus")
        # unit_name attributes differ
        self.assertFalse(marcus == self.roy)
        sigurd = Morph4("Sigurd")
        # stats are not compatible
        self.assertFalse(marcus == self.roy)
        # game_name attributes differ
        eliwood = Morph7("Eliwood")
        self.assertFalse(eliwood == self.roy)
        # equality
        roy = Morph6("Roy")
        self.assertTrue(roy == self.roy)
        # comparison_labels differ
        roy.comparison_labels[''] = None
        self.assertFalse(roy == self.roy)
        roy.comparison_labels.pop('')
        # history differs
        roy.history.append(None)
        self.assertFalse(roy == self.roy)
        roy.history.pop()
        # current_clstype attributes differ
        old_clstype = roy.current_clstype
        roy.current_clstype = ""
        self.assertFalse(roy == self.roy)
        roy.current_clstype = old_clstype
        # current_stats differ
        old_hp = roy.current_stats['HP']
        roy.current_stats['HP'] = 99
        self.assertFalse(roy == self.roy)
        roy.current_stats['HP'] = old_hp
        # current_lv attributes differ
        old_lv = roy.current_lv
        roy.current_lv = 20
        self.assertFalse(roy == self.roy)
        roy.current_lv = old_lv
        # current_cls attributes differ
        old_cls = roy.current_cls
        roy.current_cls = ""
        self.assertFalse(roy == self.roy)
        #roy.current_cls = old_cls

    def test_cap_stats__statfloor(self):
        """
        Tests that negative stat bonusses do not put a character's stat below zero.
        """
        logging.info("Morph6Test.test__cap_stats__statfloor()")
        self.roy.current_stats["HP"] = -46
        self.roy.cap_stats()
        self.assertEqual(self.roy.current_stats["HP"], 0)

    def test_level_up(self):
        """
        Tests that the current_lv and current_stats have been incremented.

        Assert:
        - current_lv = 20
        - current_stats = base_stats + (growths/100) * 19
        """
        logging.info("Morph6Test.test_level_up()")
        current_stat_copy = self.roy.current_stats.copy()
        growths = BaseMorph(6).url_to_tables['characters/growth-rates'][0].set_index("Name").loc["Roy", :]
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
        logging.info("Morph6Test.test_cap_stats()")
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
        logging.info("Morph6Test.test_promote()")
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

    def test_level_up__failures(self):
        """
        Verifies that the ValueError is raised in specific situations.
        """
        logging.info("Morph6Test.test_level_up__failures()")
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
        logging.info("Morph6Test.test_promote__failures()")
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
        logging.info("Morph6Test.test_is_maxed()")
        mock_maxed = pd.Series(index=self.roy.current_stats.index, data=[False for stat in self.roy.current_stats])
        mock_maxed['Lck'] = True
        self.roy.current_stats['Lck'] = 30
        self.assertTrue(all(self.roy.is_maxed() == mock_maxed))

    def test_is_maxed1(self):
        """
        Verifies that the pd.Series lists which stats are maxed (=True).

        Case: Luck maxes out at 30
        """
        logging.info("Morph6Test.test_is_maxed1()")
        mock_maxed = pd.Series(index=self.roy.current_stats.index, data=[False for stat in self.roy.current_stats])
        mock_maxed['Lck'] = True
        self.roy.current_stats['Lck'] = 30
        # mock promotion
        self.roy.current_clstype = "classes/promotion-gains"
        self.roy.current_cls = "Master Lord"
        self.assertTrue(all(self.roy.is_maxed() == mock_maxed))

    def test__lt__(self):
        """
        Verifies that the pd.DataFrame returned summarizes the differences between Morph objects.
        """
        logging.info("Morph6Test.test__lt__()")
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
        roy = Morph(6, "Roy")
        comparison = roy < self.roy
        self.assertIsInstance(comparison, pd.DataFrame)
        print(comparison)
        with self.assertRaises(pd.errors.InvalidIndexError):
            null = self.roy < self.roy
        with self.assertRaises(NameError):
            del null

class Morph4Test(unittest.TestCase):
    """
    Defines methods to test FE4 kids and other sort of FE4 units.
    """

    def setUp(self):
        """
        Creates a Morph of Lex!Lakche to simulate level-ups with.
        Also creates mock bases, and a Morph of Sigurd.
        """
        # create Morph of FE4 kid
        self.identifier = ("Lakche", "Lex")
        self.lakche = Morph4(*self.identifier)
        self.assertFalse(any(self.lakche.current_stats.isnull()))
        # create copy of bases for easy reference
        self.bases = self.lakche.current_stats.copy()
        #self.bases.pop("Class")
        #self.bases.pop("Lv")
        self.sigurd = Morph4("Sigurd")

    def test__init__unit_dne(self):
        """
        Tests that an AssertionError is raised if the unit provided DNE.
        """
        with self.assertRaises(KeyError):
            roy = Morph4("Roy", father_name="Eliwood")

    def test__init__father_dne(self):
        """
        Tests that a KeyError is raised if the unit is not found.
        """
        with self.assertRaises(KeyError):
            eliwood = Morph4("Lakche", father_name="Sigurd")

    def test_promote(self):
        """
        Tests that post-promotion, a unit's current level is retained.
        """
        logging.warning("Morph4Test.test_promote()")
        target_lv = 20
        self.lakche.current_lv = target_lv
        #self.assertEqual(self.lakche.current_lv, target_lv)
        self.lakche.promote()
        self.assertEqual(self.lakche.current_lv, target_lv)

    def test_level_up1(self):
        """
        Tests when an FE4 unit tries to level-up beyond max-level.
        """
        logging.warning("Morph4Test.test_level_up1()")
        # test modified level-up method
        with self.assertRaises(ValueError):
            self.lakche.level_up(99)

    def test_level_up(self):
        """
        Tests the child-implementation of level_up method.
        """
        logging.warning("Morph4Test.test_level_up()")
        # test modified level-up method
        growths = BaseMorph(4).url_to_tables["characters/growth-rates"][1].set_index(["Name", "Father"]).loc[self.identifier, :]
        expected = (1.0 * self.bases) + growths * (20 - self.lakche.current_lv) / 100
        self.lakche.level_up(20)
        self.assertTrue(all(abs(self.lakche.current_stats - expected) < 0.01))

    def test__repr__(self):
        """
        Tests that the __repr__ dunder returns a string containing:
        - History
        - Class
        - Level
        - Stats
        """
        logging.warning("Morph4Test.test__repr__()")
        repr_series = self.lakche.get_repr_series(["comparison_labels"])
        with self.assertRaises(KeyError):
            repr_series.pop("PrevClassLv1")
        self.assertEqual(repr_series.to_string(), self.lakche.__repr__())
        self.assertEqual(repr_series.pop("Name"), self.lakche.unit_name)
        self.assertEqual(repr_series.pop("Father"), self.lakche.father_name)
        self.assertEqual(repr_series.pop("Class"), self.lakche.current_cls)
        self.assertEqual(repr_series.pop("Lv"), self.lakche.current_lv)
        self.assertTrue(all(repr_series == self.lakche.current_stats))
        print(self.lakche)
        # promote, then retest
        # level_up
        self.lakche.current_lv = 20
        prevcls = self.lakche.current_cls
        # promote
        self.lakche.history.append( (self.lakche.current_cls, self.lakche.current_lv) )
        self.lakche.current_cls = "Swordmaster"
        repr_series = self.lakche.get_repr_series(["comparison_labels", "history"])
        self.assertEqual(repr_series.to_string(), self.lakche.__repr__())
        self.assertEqual(repr_series.pop("Name"), self.lakche.unit_name)
        self.assertEqual(repr_series.pop("Father"), self.lakche.father_name)
        self.assertEqual(repr_series.pop("Class"), self.lakche.current_cls)
        self.assertEqual(repr_series.pop("Lv"), self.lakche.current_lv)
        self.assertEqual(repr_series.pop("PrevClassLv1"), (prevcls, self.lakche.current_lv))
        self.assertTrue(all(repr_series == self.lakche.current_stats))
        print(self.lakche)

    def test__lt__(self):
        """
        Confirms that __lt__ dunder output is as expected.
        Lex!Lakche: Unpromoted with parent.
        Arden!Rana: Unpromoted with parent (not equal to Lakche).
        Arden!Lakche: Unpromoted with different parent.
        Alec: Unpromoted.
        Sigurd: Promoted.
        """
        logging.warning("Morph4Test.test__lt__()")
        # vs. Arden!Rana
        rana = Morph4("Rana", "Arden")
        rana_v_lakche = rana < self.lakche
        self.assertIsInstance(rana_v_lakche, pd.DataFrame)
        print(rana_v_lakche)
        # vs. Arden!Lakche
        arden_lakche = Morph4("Lakche", "Arden")
        alakche_v_llakche = arden_lakche < self.lakche
        self.assertIsInstance(alakche_v_llakche, pd.DataFrame)
        print(alakche_v_llakche)
        # vs. Alec
        alec = Morph4("Alec")
        alec.current_lv = 20
        alec.history.append( (alec.current_cls, alec.current_lv) )
        alec.current_cls = "Paladin"
        self.lakche.current_lv = 20
        self.lakche.history.append( (self.lakche.current_cls, self.lakche.current_lv))
        self.lakche.current_cls = "Swordmaster"
        alec_v_lakche = alec < self.lakche
        self.assertIsInstance(alec_v_lakche, pd.DataFrame)
        print(alec_v_lakche)
        # vs. Sigurd
        sigurd = Morph4("Sigurd")
        sigurd.current_lv = 20
        sigurd_v_lakche = (sigurd < self.lakche)
        self.assertIsInstance(alec_v_lakche, pd.DataFrame)
        print(sigurd_v_lakche)

    def test_promote(self):
        """
        Tests the child-implementation of promote method.

        Note: Not really necessary, since it's not affected.
        """
        logging.warning("Morph4Test.test_promote()")
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
        """
        Sets up fixtures for Lara shenanigans. 
        """
        self.lara = Morph5("Lara")
        self.assertFalse(any(self.lara.current_stats.isnull()))
        self.bases = self.lara.current_stats.copy()
        # initialize promo bonuses for all scenarios
        promo_table = self.lara.url_to_tables["classes/promotion-gains"][0].set_index(["Class", "Promotion"])
        self.dancer__to__thief_fighter = promo_table.loc[("Dancer", "Thief Fighter"), :].reindex(self.bases.index, fill_value=0.0)
        self.thief__to__dancer = promo_table.loc[("Thief", "Dancer"), :].reindex(self.bases.index, fill_value=0.0)
        self.thief_fighter__to__dancer = promo_table.loc[("Thief Fighter", "Dancer"), :].reindex(self.bases.index, fill_value=0.0)
        self.thief__to__thief_fighter = promo_table.loc[("Thief", "Thief Fighter"), :].reindex(self.bases.index, fill_value=0.0)

    @patch("pathlib.Path.exists")
    def test_level_up__failures(self, mock_exists):
        """
        Tests the errors that can appear as a result of bad leveling-up.

        1. target_lv > max_lv
        2. target_lv < current_lv
        3. scroll file DNE
        """
        logging.warning("Morph5Test.test_level_up__failures()")
        mock_exists.return_value = False
        with self.assertRaises(ValueError):
            self.lara.level_up(99)
        with self.assertRaises(ValueError):
            self.lara.level_up(2)
        self.lara.equipped_scrolls.append(None)
        with self.assertRaises(FileNotFoundError):
            self.lara.level_up(20)

    def test_promote1(self):
        """
        Tests longest promotion path:
        - Thief -> Thief Fighter -> Dancer -> Thief Fighter
        """
        logging.warning("Morph5Test.test_promote1()")
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
            # Lara can promote no further
            self.lara.promote()

    def test_promote2(self):
        """
        Tests shortest promotion path:
        - Thief -> Dancer -> Thief Fighter
        """
        logging.warning("Morph5Test.test_promote2()")
        # Thief -> Dancer -> Thief Fighter
        self.lara.promo_cls = "Dancer"
        self.assertEqual(self.lara.current_lv, 2)
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
            # Lara can promote no further
            self.lara.promote()

    def test_scroll_lvup(self):
        """
        Verifies that scroll-boosted level-ups are simulated as expected.
        """
        logging.warning("Morph5Test.test_scroll_lvup()")
        self.lara.equipped_scrolls.append("Odo")
        base_skl = self.lara.current_stats["Skl"]
        skl_growth = 0.5
        odo_skl_growth  = 0.3
        num_levels = 10
        self.lara.level_up(self.lara.current_lv + num_levels)
        self.assertEqual(self.lara.current_stats["Skl"], base_skl + num_levels * (skl_growth + odo_skl_growth))
        self.lara.equipped_scrolls[0] = ""
        # assert that this fails as expected
        with self.assertRaises(KeyError):
            self.lara.level_up(self.lara.current_lv + 1)
        for index in range(7):
            self.lara.equipped_scrolls.append(None)
        max_inventory_size = 7
        self.assertGreater(len(self.lara.equipped_scrolls), max_inventory_size)
        with self.assertRaises(AssertionError):
            self.lara.level_up(self.lara.current_lv + 1)

class Morph7Test(unittest.TestCase):
    """
    Defines methods to test FE7-exclusive exceptions, as well as 'Campaign' rows in __lt__ dunder.

    i.e. main!Wallace and tutorial!Wallace.
    """

    def setUp(self):
        """
        Set up Wallace-Morphs here.
        """
        # initialize both versions of Wallace
        self.wallace0 = Morph7("Wallace", lyn_mode=True)
        self.wallace1 = Morph7("Wallace", lyn_mode=False)
        self.assertFalse(any(self.wallace0.current_stats.isnull()))
        self.assertFalse(any(self.wallace1.current_stats.isnull()))
        self.growths = BaseMorph(7).url_to_tables["characters/growth-rates"][0].set_index("Name").loc["Wallace", :]

    def test__lt__(self):
        """
        Test that the output contains a 'Campaign' row, and that that row lists the values appropriately.
        """
        logging.warning("Morph7Test.test__lt__()")
        lyn = Morph7("Lyn", lyn_mode=True)
        guy = Morph7("Guy (HM)")
        florina = Morph7("Florina")
        florina.current_lv = 20
        florina.history.append( (florina.current_cls, florina.current_lv) )
        florina.current_cls = "Falcoknight"
        lyn.current_lv = 20
        lyn.history.append( (lyn.current_cls, lyn.current_lv) )
        lyn.current_cls = "Blade Lord"
        #lyn.level_up(20)
        #lyn.promote()
        lyn_v_guy = lyn < guy
        lyn_v_florina = lyn < florina
        self.assertIsInstance(lyn_v_guy, pd.DataFrame)
        self.assertIsInstance(lyn_v_florina, pd.DataFrame)
        self.assertEqual(lyn_v_guy.at["Campaign", "Lyn"], "Tutorial")
        self.assertEqual(lyn_v_guy.at["Campaign", "Guy"], "-")
        self.assertEqual(lyn_v_guy.at["Hard Mode", "Guy"], True)
        self.assertEqual(lyn_v_guy.at["Hard Mode", "Lyn"], "-")
        self.assertEqual(lyn_v_florina.at["Campaign", "Lyn"], "Tutorial")
        self.assertEqual(lyn_v_florina.at["Campaign", "Florina"], "Main")
        print(lyn_v_guy)
        print(lyn_v_florina)

    def test__repr__(self):
        """
        Tests that the __repr__ dunder returns a string containing:
        - History
        - Class
        - Level
        - Stats
        """
        logging.warning("Morph7Test.test__repr__()")
        guy = Morph7("Guy")
        repr_series = guy.get_repr_series(['comparison_labels'])
        with self.assertRaises(KeyError):
            repr_series.pop("PrevClassLv1")
        self.assertEqual(repr_series.to_string(), guy.__repr__())
        print(guy)
        self.assertEqual(repr_series.pop("Name"), guy.unit_name)
        self.assertEqual(repr_series.pop("Hard Mode"), False)
        self.assertEqual(repr_series.pop("Class"), guy.current_cls)
        self.assertEqual(repr_series.pop("Lv"), guy.current_lv)
        self.assertTrue(all(repr_series == guy.current_stats))
        # promote and retest
        prevcls = guy.current_cls
        guy.current_lv = 20
        guy.history.append( (guy.current_cls, guy.current_lv) )
        guy.current_cls = "Swordmaster"
        #guy.promote()
        repr_series = guy.get_repr_series(['comparison_labels', 'history'])
        self.assertEqual(repr_series.to_string(), guy.__repr__())
        print(guy)
        self.assertEqual(repr_series.pop("Name"), guy.unit_name)
        self.assertEqual(repr_series.pop("PrevClassLv1"), (prevcls, 20))
        self.assertEqual(repr_series.pop("Hard Mode"), False)
        self.assertEqual(repr_series.pop("Class"), guy.current_cls)
        self.assertEqual(repr_series.pop("Lv"), guy.current_lv)
        self.assertTrue(all(repr_series == guy.current_stats))

    def test_get_repr_series__comparison_labels(self):
        """
        Shows Hard Mode indicator when applicable.
        """
        guy = Morph7("Guy (HM)")
        repr_series = guy.get_repr_series(["comparison_labels"])
        self.assertIn("Hard Mode", repr_series.index)

class Morph8Test(unittest.TestCase):
    """
    Defines tests for scrub units. Also defines tests to see output of __lt__ dunders for them.
    """

    def setUp(self):
        """
        Sets Amelia up with a history of three two class changes.
        """
        self.amelia = Morph8("Amelia") 
        self.assertFalse(any(self.amelia.current_stats.isnull()))
        self.amelia.level_up(10)
        self.amelia.promo_cls = "Cavalier (F)"
        self.amelia.promote()
        self.amelia.level_up(20)
        self.amelia.promo_cls = "Paladin (F)"
        self.amelia.promote()
        self.amelia.level_up(20)

    def test__lt__0(self):
        """
        Prints output of __lt__ dunder with:
        - A unit with two class changes
        - A unit with no class changes
        """
        logging.warning("Morph8Test.test__lt__0()")
        seth = Morph8("Seth") 
        seth.current_lv = 20
        #seth.level_up(20)
        amelia_v_seth = self.amelia < seth
        self.assertIsInstance(amelia_v_seth, pd.DataFrame)
        print(amelia_v_seth)

    def test__lt__1(self):
        """
        Prints output of __lt__ dunder with:
        - A unit with two class changes
        - A unit with one class change
        """
        logging.warning("Morph8Test.test__lt__1()")
        ephraim = Morph8("Ephraim")
        ephraim.current_lv = 20
        #ephraim.level_up(20)
        ephraim.history.append( (ephraim.current_cls, ephraim.current_lv) )
        ephraim.current_cls = "Great Lord (M)"
        #ephraim.promote()
        #ephraim.level_up(20)
        amelia_v_ephraim = self.amelia < ephraim
        self.assertIsInstance(amelia_v_ephraim, pd.DataFrame)
        print(amelia_v_ephraim)

    def test__lt__2(self):
        """
        Prints output of __lt__ dunder with:
        - A unit with two class changes
        - A unit with two class changes
        """
        logging.warning("Morph8Test.test__lt__2()")
        ross = Morph8("Ross") 
        ross.current_lv = 10
        #ross.level_up(10)
        ross.history.append( (ross.current_cls, ross.current_lv) )
        ross.current_cls = "Pirate"
        #ross.promo_cls = "Pirate"
        #ross.promote()
        print(ross.current_clstype)
        ross.current_lv = 20
        #ross.level_up(20)
        ross.history.append( (ross.current_cls, ross.current_lv) )
        ross.current_cls = "Berserker"
        #ross.promote()
        ross.current_lv = 20
        #ross.level_up(20)
        #ross.cap_stats()
        print(ross.is_maxed())
        amelia_v_ross = self.amelia < ross
        self.assertIsInstance(amelia_v_ross, pd.DataFrame)
        print(amelia_v_ross)

    def test_promote__nopromocls(self):
        """
        Asserts that KeyError is raised if the promo_cls attribute is not specified when required.
        """
        ross = Morph8("Ross")
        self.assertIsNone(ross.promo_cls)
        ross.current_lv = 10
        with self.assertRaises(KeyError):
            ross.promote()

    def test_is_maxed(self):
        """
        Tests that the the is_maxed call works properly.
        """
        self.amelia.cap_stats()
        is_maxed = self.amelia.is_maxed()
        self.assertEqual(is_maxed.dtype, bool)


class Morph9Test(unittest.TestCase):
    """
    Defines tests for leveling up, promoting, and capping stats.
    """

    def setUp(self):
        """
        Creates a Morph object, with the option specified for full coverage.
        """
        self.ike = Morph9("Ike", datadir_root="data")
        self.assertFalse(any(self.ike.current_stats.isnull()))

if __name__ == '__main__':
    module = Morph6Test
    findstr = "test__eq__"
    unittest.main(
        defaultTest=[test for test in dir(module) if findstr in test],
        module=module,
    )
