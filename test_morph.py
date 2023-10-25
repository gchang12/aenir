#!/usr/bin/python3
"""
Tests the aenir.morph.Morph class methods.
"""

import unittest
import logging
import json

import pandas as pd


from aenir.morph import Morph, Morph4, Morph5, Morph6, Morph7, Morph8, Morph9

logging.basicConfig(level=logging.DEBUG, filename="aenirtesting.log")

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

    def test_fe4_units(self):
        """
        Verifies that all units can be leveled-up, stat-capped, and promoted.
        """
        base = Morph(4, "Sigurd")
        def not_a_kid(name):
            return name not in base.url_to_tables["characters/base-stats"][1]["Name"]
        for unit_name in filter(not_a_kid, base.get_character_list()):
            fe4_unit = Morph(4, unit_name)
            try:
                logging.warning("Leveling '%s' to level 20.", fe4_unit.unit_name)
                fe4_unit.level_up(20)
            except ValueError as exc:
                logging.warning("'%s' is at level 20 already.", fe4_unit.unit_name)
            fe4_unit.cap_stats()
            try:
                prevcls = fe4_unit.current_cls
                fe4_unit.promote()
                logging.warning("Changed class of '%s' from '%s' to '%s'.", fe4_unit.unit_name, prevcls, fe4_unit.current_cls)
            except ValueError as exc:
                logging.warning("'%s' cannot promote", fe4_unit.unit_name)
            try:
                logging.warning("Leveling '%s' to level 30.", fe4_unit.unit_name)
                fe4_unit.level_up(30)
            except ValueError as exc:
                logging.warning("'%s' is at level 30 already.", fe4_unit.unit_name)
            fe4_unit.cap_stats()

    def test_fe9_units(self):
        """
        Verifies that all units can be leveled-up, stat-capped, and promoted.
        """
        game_num = 9
        base = Morph(game_num, "Ike")
        for unit_name in base.get_character_list():
            fe9_unit = Morph(game_num, unit_name)
            try:
                logging.warning("Leveling '%s' to level 20.", fe9_unit.unit_name)
                fe9_unit.level_up(20)
            except ValueError as exc:
                logging.warning("'%s' is at level 20 already.", fe9_unit.unit_name)
            fe9_unit.cap_stats()
            try:
                prevcls = fe9_unit.current_cls
                fe9_unit.promote()
                self.assertEqual(fe9_unit.current_lv, 1)
                logging.warning("Changed class of '%s' from '%s' to '%s'.", fe9_unit.unit_name, prevcls, fe9_unit.current_cls)
            except ValueError as exc:
                logging.warning("'%s' cannot promote", fe9_unit.unit_name)
            fe9_unit.cap_stats()
            try:
                logging.warning("Leveling '%s' to level 20.", fe9_unit.unit_name)
                fe9_unit.level_up(20)
            except ValueError as exc:
                logging.warning("'%s' is at level 20 already.", fe9_unit.unit_name)
            fe9_unit.cap_stats()

    def test_fe8_units(self):
        """
        Verifies that most units can be leveled-up, stat-capped, and promoted.

        Exceptions: Ross, Amelia, Ewan
        """
        game_num = 8
        base = Morph(game_num, "Ephraim")
        branched_promo = {}
        junior_units = ("Ross", "Amelia", "Ewan")
        for unit_name in base.get_character_list():
            if unit_name in junior_units:
                continue
            try:
                fe8_unit = Morph(game_num, unit_name)
            except KeyError:
                fe8_unit = Morph(game_num, unit_name, tableindex=1)
            try:
                logging.warning("Leveling '%s' to level 20.", fe8_unit.unit_name)
                fe8_unit.level_up(20)
            except ValueError as exc:
                logging.warning("'%s' is at level 20 already.", fe8_unit.unit_name)
            fe8_unit.cap_stats()
            try:
                prevcls = fe8_unit.current_cls
                fe8_unit.promote()
                self.assertEqual(fe8_unit.current_lv, 1)
                logging.warning("Changed class of '%s' from '%s' to '%s'.", fe8_unit.unit_name, prevcls, fe8_unit.current_cls)
            except (ValueError, KeyError) as exc:
                if fe8_unit.target_stats is None:
                    logging.warning("'%s' cannot promote", fe8_unit.unit_name)
                else:
                    branched_promo[unit_name] = tuple(fe8_unit.target_stats["Promotion"])
                    logging.warning("'%s' has branched promotion. Deferring for later.", fe8_unit.unit_name)
                    continue
            fe8_unit.cap_stats()
            try:
                logging.warning("Leveling '%s' to level 20.", fe8_unit.unit_name)
                fe8_unit.level_up(20)
            except ValueError as exc:
                logging.warning("'%s' is at level 20 already.", fe8_unit.unit_name)
            fe8_unit.cap_stats()
        for unit_name, promolist in branched_promo.items():
            for promocls in promolist:
                fe8_unit = Morph(8, unit_name)
                fe8_unit.level_up(20)
                fe8_unit.cap_stats()
                fe8_unit.promo_cls = promocls
                fe8_unit.promote()
                fe8_unit.cap_stats()
                fe8_unit.level_up(20)
                fe8_unit.cap_stats()

    def test_villager_ross(self):
        """
        Verifies that Ross can be leveled-up, stat-capped, and promoted.

        Covers all possible promotion paths he may take.
        """
        game_num = 8
        promo_paths = [
            ["Fighter", "Warrior"],
            ["Fighter", "Hero"],
            ["Pirate", "Berserker"],
            ["Pirate", "Warrior"],
            ["Journeyman (2)", "Hero"],
            ["Journeyman (2)", "Journeyman (3)"],
        ]
        for promo in promo_paths:
            promocp = promo.copy()
            ross = Morph(game_num, "Ross")
            ross.level_up(10)
            ross.cap_stats()
            ross.promo_cls = promocp.pop(0)
            ross.promote()
            ross.cap_stats()
            ross.level_up(20)
            ross.cap_stats()
            ross.promo_cls = promocp.pop(0)
            ross.promote()
            ross.cap_stats()
            ross.level_up(20)
            ross.cap_stats()

    def test_villager_ewan(self):
        """
        Verifies that Ewan can be leveled-up, stat-capped, and promoted.

        Covers all possible promotion paths he may take.
        """
        game_num = 8
        promo_paths = [
            ["Mage (M)", "Sage (M)"],
            ["Mage (M)", "Mage Knight (M)"],
            ["Shaman (M)", "Druid"],
            ["Shaman (M)", "Summoner"],
            ["Pupil (2)", "Sage (M)"],
            ["Pupil (2)", "Pupil (3)"],
        ]
        for promo in promo_paths:
            promocp = promo.copy()
            ewan = Morph(game_num, "Ewan")
            ewan.level_up(10)
            ewan.cap_stats()
            ewan.promo_cls = promocp.pop(0)
            ewan.promote()
            ewan.cap_stats()
            ewan.level_up(20)
            ewan.cap_stats()
            ewan.promo_cls = promocp.pop(0)
            ewan.promote()
            ewan.cap_stats()
            ewan.level_up(20)
            ewan.cap_stats()

    def test_villager_amelia(self):
        """
        Verifies that Amelia can be leveled-up, stat-capped, and promoted.

        Covers all possible promotion paths she may take.
        """
        game_num = 8
        promo_paths = [
            ["Cavalier (F)", "Paladin (F)"],
            ["Cavalier (F)", "Great Knight (F)"],
            ["Knight (F)", "General (F)"],
            ["Knight (F)", "Great Knight (F)"],
            ["Recruit (2)", "Paladin (F)"],
            ["Recruit (2)", "Recruit (3)"],
        ]
        for promo in promo_paths:
            promocp = promo.copy()
            amelia = Morph(game_num, "Amelia")
            amelia.level_up(10)
            amelia.cap_stats()
            amelia.promo_cls = promocp.pop(0)
            amelia.promote()
            amelia.cap_stats()
            amelia.level_up(20)
            amelia.cap_stats()
            amelia.promo_cls = promocp.pop(0)
            amelia.promote()
            amelia.cap_stats()
            amelia.level_up(20)
            amelia.cap_stats()

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
        self.bases = self.lakche.url_to_tables["characters/base-stats"][1].set_index(["Name", "Father"]).loc[self.identifier, :].copy()
        self.bases.pop("Class")
        self.bases.pop("Lv")
        self.sigurd = Morph4("Sigurd")

    def test__lt__(self):
        """
        Confirms that __lt__ dunder output is as expected.

        Lex!Lakche: Unpromoted with parent.
        Arden!Rana: Unpromoted with parent (not equal to Lakche).
        Arden!Lakche: Unpromoted with different parent.
        Alec: Unpromoted.
        Sigurd: Promoted.
        """
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
        alec.level_up(20)
        alec.promote()
        self.lakche.level_up(20)
        self.lakche.promote()
        alec_v_lakche = alec < self.lakche
        self.assertIsInstance(alec_v_lakche, pd.DataFrame)
        print(alec_v_lakche)
        # vs. Sigurd
        sigurd = Morph4("Sigurd")
        sigurd.level_up(20)
        sigurd_v_lakche = (sigurd < self.lakche)
        self.assertIsInstance(alec_v_lakche, pd.DataFrame)
        print(sigurd_v_lakche)

    def test_level_up(self):
        """
        Tests the child-implementation of level_up method.
        """
        # test modified level-up method
        growths = self.lakche.url_to_tables["characters/growth-rates"][1].set_index(["Name", "Father"]).loc[self.identifier, :]
        expected = (1.0 * self.bases) + growths * (20 - self.lakche.current_lv) / 100
        self.lakche.level_up(20)
        self.assertTrue(all(abs(self.lakche.current_stats - expected) < 0.01))

    def test_promote(self):
        """
        Tests the child-implementation of promote method.

        Note: Not really necessary, since it's not affected.
        """
        # test FE4 promotion
        current_lv = 20
        self.lakche.current_lv = current_lv
        self.lakche.promote()
        self.assertEqual(self.lakche.current_cls, "Swordmaster")
        self.assertEqual(self.lakche.current_lv, current_lv)
        temp_promo = self.lakche.url_to_tables['classes/promotion-gains'][0].set_index(["Class", "Promotion"]).loc[("Swordfighter", "Swordmaster"), :].reindex(self.bases.index, fill_value=0.0) * 1.0
        self.assertTrue(all(abs(self.lakche.current_stats - self.bases - temp_promo) < 0.01))

    def test__repr__(self):
        """
        Tests that the __repr__ dunder returns a string containing:

        - History
        - Class
        - Level
        - Stats
        """
        repr_series = self.lakche.get_repr_series()
        with self.assertRaises(KeyError):
            print(repr_series.pop("PrevClassLv1"))
        self.assertEqual(repr_series.to_string(), self.lakche.__repr__())
        self.assertEqual(repr_series.pop("Name"), self.lakche.unit_name)
        self.assertEqual(repr_series.pop("Father"), self.lakche.father_name)
        self.assertEqual(repr_series.pop("Class"), self.lakche.current_cls)
        self.assertEqual(repr_series.pop("Lv"), self.lakche.current_lv)
        self.assertTrue(all(repr_series == self.lakche.current_stats))
        print(self.lakche)
        # promote, then retest
        self.lakche.level_up(20)
        prevcls = self.lakche.current_cls
        self.lakche.promote()
        repr_series = self.lakche.get_repr_series()
        self.assertEqual(repr_series.to_string(), self.lakche.__repr__())
        self.assertEqual(repr_series.pop("Name"), self.lakche.unit_name)
        self.assertEqual(repr_series.pop("Father"), self.lakche.father_name)
        self.assertEqual(repr_series.pop("Class"), self.lakche.current_cls)
        self.assertEqual(repr_series.pop("Lv"), self.lakche.current_lv)
        self.assertEqual(repr_series.pop("PrevClassLv1"), (prevcls, self.lakche.current_lv))
        self.assertTrue(all(repr_series == self.lakche.current_stats))
        print(self.lakche)

    def test_all_units(self):
        """
        Tests that all units can be leveled-up, stat-capped, and promoted.
        """
        father_list = set(self.lakche.url_to_tables["characters/base-stats"][1]["Father"])
        for unit_name in set(self.lakche.url_to_tables["characters/base-stats"][1]["Name"]):
            for father in father_list:
                kid_unit = Morph4(unit_name, father)
                try:
                    logging.warning("Maxing out the level of '%s!%s'.", kid_unit.father_name, kid_unit.unit_name)
                    kid_unit.level_up(20)
                except ValueError:
                    logging.warning("'%s!%s' is already at max-level.", kid_unit.father_name, kid_unit.unit_name)
                kid_unit.cap_stats()
                try:
                    prevcls = kid_unit.current_cls
                    kid_unit.promote()
                    logging.warning("Promoted '%s!%s' from '%s' to '%s'.", kid_unit.father_name, kid_unit.unit_name, prevcls, kid_unit.current_cls)
                except ValueError as exc:
                    logging.warning("'%s!%s' cannot promote.", kid_unit.father_name, kid_unit.unit_name)
                kid_unit.cap_stats()
                try:
                    logging.warning("Maxing out the level of '%s!%s'.", kid_unit.father_name, kid_unit.unit_name)
                    kid_unit.level_up(20)
                except ValueError:
                    logging.warning("'%s!%s' is already at max-level.", kid_unit.father_name, kid_unit.unit_name)
                kid_unit.cap_stats()

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

    def test_promote1(self):
        """
        Tests longest promotion path:
        - Thief -> Thief Fighter -> Dancer -> Thief Fighter
        """
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

    def test_all_units(self):
        """
        Tests that all units can be leveled-up, stat-capped, and promoted.
        """
        for unit_name in self.lara.get_character_list():
            if unit_name == "Lara":
                continue
            fe5_unit = Morph5(unit_name)
            if fe5_unit.current_lv < 20:
                logging.warning(f"Maxing out level of '{fe5_unit.unit_name}'.")
                fe5_unit.level_up(20)
            else:
                logging.warning(f"'{fe5_unit.unit_name}' is already at max-level.")
            fe5_unit.cap_stats()
            try:
                prevcls = fe5_unit.current_cls
                fe5_unit.promote()
                logging.warning(f"'{fe5_unit.unit_name}' has promoted from '{prevcls}' to '{fe5_unit.current_cls}'.")
            except ValueError:
                logging.warning(f"'{fe5_unit.unit_name}' cannot promote.")
            if "Thief" in fe5_unit.current_cls:
                logging.warning(f"Checking if '{fe5_unit.unit_name}' can promote into a 'Dancer'...")
                with self.assertRaises(ValueError):
                    fe5_unit.promote()
                logging.warning(f"'{fe5_unit.unit_name}' cannot promote further.")
            fe5_unit.cap_stats()
            if fe5_unit.current_lv < 20:
                logging.warning(f"Maxing out level of '{fe5_unit.unit_name}'.")
                fe5_unit.level_up(20)
            else:
                logging.warning(f"'{fe5_unit.unit_name}' is already at max-level.")
            fe5_unit.cap_stats()

    def test_scroll_lvup(self):
        """
        Verifies that scroll-boosted level-ups are simulated as expected.
        """
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
        self.growths = self.wallace0.url_to_tables["characters/growth-rates"][0].set_index("Name").loc["Wallace", :]

    def test__repr__(self):
        """
        Tests that the __repr__ dunder returns a string containing:

        - History
        - Class
        - Level
        - Stats
        """
        guy = Morph7("Guy")
        repr_series = guy.get_repr_series()
        with self.assertRaises(KeyError):
            print(repr_series.pop("PrevClassLv1"))
        self.assertEqual(repr_series.to_string(), guy.__repr__())
        print(guy)
        self.assertEqual(repr_series.pop("Name"), guy.unit_name)
        self.assertEqual(repr_series.pop("Hard Mode"), False)
        self.assertEqual(repr_series.pop("Class"), guy.current_cls)
        self.assertEqual(repr_series.pop("Lv"), guy.current_lv)
        self.assertTrue(all(repr_series == guy.current_stats))
        # promote and retest
        prevcls = guy.current_cls
        guy.level_up(20)
        guy.promote()
        repr_series = guy.get_repr_series()
        self.assertEqual(repr_series.to_string(), guy.__repr__())
        print(guy)
        self.assertEqual(repr_series.pop("Name"), guy.unit_name)
        self.assertEqual(repr_series.pop("PrevClassLv1"), (prevcls, 20))
        self.assertEqual(repr_series.pop("Hard Mode"), False)
        self.assertEqual(repr_series.pop("Class"), guy.current_cls)
        self.assertEqual(repr_series.pop("Lv"), guy.current_lv)
        self.assertTrue(all(repr_series == guy.current_stats))

    def test__lt__(self):
        """
        Test that the output contains a 'Campaign' row, and that that row lists the values appropriately.
        """
        lyn = Morph7("Lyn", lyn_mode=True)
        guy = Morph7("Guy (HM)")
        florina = Morph7("Florina")
        florina.level_up(20)
        florina.promote()
        lyn.level_up(20)
        lyn.promote()
        lyn_v_guy = lyn < guy
        lyn_v_florina = lyn < florina
        self.assertIsInstance(lyn_v_guy, pd.DataFrame)
        self.assertIsInstance(lyn_v_florina, pd.DataFrame)
        self.assertEqual(lyn_v_guy.at["Campaign", "Lyn"], "Tutorial")
        self.assertEqual(lyn_v_guy.at["Campaign", "Guy (HM)"], "-")
        self.assertEqual(lyn_v_guy.at["Hard Mode", "Guy (HM)"], True)
        self.assertEqual(lyn_v_guy.at["Hard Mode", "Lyn"], "-")
        self.assertEqual(lyn_v_florina.at["Campaign", "Lyn"], "Tutorial")
        self.assertEqual(lyn_v_florina.at["Campaign", "Florina"], "Main")
        print(lyn_v_guy)
        print(lyn_v_florina)

    def test_tutorial_wallace(self):
        """
        Tests that Tutorial!Wallace can be leveled-up, stat-capped, and promoted.
        """
        # max out level -> promote -> cap stats
        bases = self.wallace0.current_stats.copy()
        # test level-up
        self.wallace0.level_up(20)
        self.wallace0.cap_stats()
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
        """
        Tests that Main!Wallace can be leveled-up, stat-capped, and promoted.
        """
        # fail: promote
        self.assertEqual("classes/promotion-gains", self.wallace1.current_clstype)
        with self.assertRaises(ValueError):
            self.wallace1.promote()
        # test: level-up
        bases = self.wallace1.current_stats.copy()
        self.wallace1.level_up(20)
        running_total = self.growths.copy() * 19.0 / 100
        self.assertTrue(all(abs(self.wallace1.current_stats - bases - running_total) < 0.01))
        self.wallace1.cap_stats()

    def test_all_units(self):
        """
        Tests that all units can be leveled-up, stat-capped, and promoted.
        """
        for unit_name in self.wallace0.get_character_list():
            if unit_name == "Nils":
                continue
            fe7_unit = Morph7(unit_name, lyn_mode=False)
            try:
                if fe7_unit.current_lv < 20:
                    fe7_unit.level_up(20)
                else:
                    logging.info(f"'{unit_name}' is already at max-level.")
            except ValueError as exc:
                raise ValueError(f"'{fe7_unit.unit_name}' has current_lv = '{fe7_unit.current_lv}'")
            fe7_unit.cap_stats()
            prevcls = fe7_unit.current_cls
            try:
                fe7_unit.promote()
                logging.info(f"'{unit_name}' has been promoted from '{prevcls}' to '{fe7_unit.current_cls}'.")
            except ValueError:
                logging.info(f"'{unit_name}' cannot promote.")
            fe7_unit.cap_stats()
            if fe7_unit.current_lv < 20:
                fe7_unit.level_up(20)
            else:
                logging.info(f"'{unit_name}' is already at max-level.")
            fe7_unit.cap_stats()

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
        seth = Morph8("Seth") 
        seth.level_up(20)
        amelia_v_seth = self.amelia < seth
        self.assertIsInstance(amelia_v_seth, pd.DataFrame)
        print(amelia_v_seth)

    def test__lt__1(self):
        """
        Prints output of __lt__ dunder with:
        - A unit with two class changes
        - A unit with one class change
        """
        ephraim = Morph8("Ephraim")
        ephraim.level_up(20)
        ephraim.promote()
        ephraim.level_up(20)
        amelia_v_ephraim = self.amelia < ephraim
        self.assertIsInstance(amelia_v_ephraim, pd.DataFrame)
        print(amelia_v_ephraim)

    def test__lt__2(self):
        """
        Prints output of __lt__ dunder with:
        - A unit with two class changes
        - A unit with two class changes
        """
        ross = Morph8("Ross") 
        ross.level_up(10)
        ross.promo_cls = "Pirate"
        ross.promote()
        ross.level_up(20)
        ross.promo_cls = "Berserker"
        ross.promote()
        ross.level_up(20)
        amelia_v_ross = self.amelia < ross
        self.assertIsInstance(amelia_v_ross, pd.DataFrame)
        print(amelia_v_ross)


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

    def test_all_units(self):
        """
        Performs a shallow test: each unit is put through a maxing journey.

        Assert: final > bases
        """
        ltable = "characters__base_stats"
        rtable = "classes__promotion_gains"
        with open(
                str(self.ike.home_dir.joinpath(f"{ltable}-JOIN-{rtable}.json")),
                encoding='utf-8') as rfile:
            promocls_dict = json.load(rfile)
        bases = self.ike.url_to_tables['characters/base-stats'][0].set_index("Name")
        bases.pop("Class")
        bases.pop("Lv")
        for unitname in self.ike.url_to_tables['characters/growth-rates'][0]["Name"]:
            unit = Morph(9, unitname)
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

if __name__ == '__main__':
    module = Morph9Test
    findstr = "test_"
    unittest.main(
        defaultTest=[test for test in dir(module) if findstr in test],
        module=module,
    )
