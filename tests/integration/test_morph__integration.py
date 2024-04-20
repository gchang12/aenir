#!/usr/bin/python3
"""
Contains integration tests for Morph* objects
"""

from unittest.mock import patch
import unittest
import logging
import json

import pandas as pd


from aenir._basemorph import BaseMorph
from aenir.morph import Morph, Morph4, Morph5, Morph6, Morph7, Morph8, Morph9

logging.basicConfig(level=logging.CRITICAL)


class Morph6IntegrationTest(unittest.TestCase):
    """
    Runs through potential simulations of stat comparisons.
    """

    def setUp(self):
        """
        Creates a Morph object, with the option specified for full coverage.
        """
        self.roy = Morph(6, "Roy")
        self.assertFalse(any(self.roy.current_stats.isnull()))
        # create a copy of Roy's stats, level-up, cap, and assert that the bonuses have been applied
        # create a copy of everyone's stats
        # put them through the whole: level-up 'til max, try to promote: level-up 'til max

    def test_roy(self):
        """
        In-depth test of leveling up and promoting Roy.
        Tests for stat equality at the following checkpoints:
        - Lv20 Lord
        - Lv20 Master Lord
        """
        logging.info("Morph6Test.test_roy()")
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
        logging.info("Morph6Test.test_all_units()")
        ltable = "characters__base_stats"
        rtable = "classes__promotion_gains"
        with open(
                str(self.roy.home_dir.joinpath(f"{ltable}-JOIN-{rtable}.json")),
                encoding='utf-8') as rfile:
            promocls_dict = json.load(rfile)
        for unitname in self.roy.get_character_list():
            unit = Morph(6, unitname)
            bases = unit.current_stats.copy()
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
            self.assertTrue(any(unit.current_stats > bases))

    def test_fe4_units(self):
        """
        Verifies that all units can be leveled-up, stat-capped, and promoted.
        """
        logging.info("Morph6Test.test_fe4_units()")
        base = Morph4("Sigurd")
        def not_a_kid(name):
            return name not in BaseMorph(4).url_to_tables["characters/base-stats"][1]["Name"].to_list()
        for unit_name in filter(not_a_kid, base.get_character_list()):
            fe4_unit = Morph4(unit_name)
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
        logging.info("Morph6Test.test_fe9_units()")
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
        logging.info("Morph6Test.test_fe8_units()")
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
        logging.info("Morph6Test.test_villager_ross()")
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
        logging.info("Morph6Test.test_villager_ewan()")
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
        logging.info("Morph6Test.test_villager_amelia()")
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

class Morph4IntegrationTest(unittest.TestCase):
    """
    Runs through potential simulations of stat comparisons.
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

    def test_get_maxlv(self):
        """
        Tests if setting targetstats attribute affects any operations.
        """
        maxlv = self.lakche.get_maxlv()
        self.assertEqual(maxlv, 20)
        self.lakche.level_up(20)
        self.assertEqual(maxlv, 20)
        self.lakche.promote()
        maxlv = self.lakche.get_maxlv()
        self.assertEqual(maxlv, 30)

    def test_static_units(self):
        """
        All non-kid units can be levelled up, promoted, and such.
        """
        unit_factory = BaseMorph(4)
        src_tablename = "characters/base-stats"
        staticunit_list = unit_factory.url_to_tables[src_tablename][0]["Name"].to_list()
        for unit_name in staticunit_list:
            unit = Morph4(unit_name)
            try:
                logging.info("Trying to max out level for %s.", unit.unit_name)
                unit.level_up(20)
            except ValueError:
                logging.warning("%s is already at max-level.", unit.unit_name)
            unit.cap_stats()
            try:
                prevcls = unit.current_cls
                logging.info("Trying to promote %s from %s to %s.", unit.unit_name, prevcls, unit.current_cls)
                unit.promote()
            except ValueError as exc:
                logging.warning("%s cannot promote.", unit.unit_name)
            unit.cap_stats()
            try:
                logging.warning("Trying to max out level for %s.", unit.unit_name)
                unit.level_up(20)
            except ValueError:
                logging.warning("%s is already at max-level.", unit.unit_name)
            unit.cap_stats()


    def test_kid_units(self):
        """
        Tests that all kid units can be leveled-up, stat-capped, and promoted.
        """
        unit_factory = BaseMorph(4)
        src_tablename = "characters/base-stats"
        father_list = set(unit_factory.url_to_tables[src_tablename][1].pop("Father"))
        kid_list = set(unit_factory.url_to_tables[src_tablename][1].pop("Name"))
        unit_factory.url_to_tables.clear()
        for unit_name in kid_list:
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

class Morph5IntegrationTest(unittest.TestCase):
    """
    Runs through potential simulations of stat comparisons.
    """

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

    def test_lara(self):
        """
        Tests Lara's two promotion paths:
        - Thief -> Dancer -> Thief Fighter
        - Thief -> Thief Fighter -> Dancer -> Thief Fighter
        """
        # Thief
        lara1 = Morph5("Lara")
        self.assertLess(lara1.current_lv, 10)
        lara1.promo_cls = "Dancer"
        lara1.promote()
        # Dancer
        lara1.cap_stats()
        lara1.level_up(10)
        #lara1.promo_cls = "Thief Fighter"
        # Thief Fighter
        lara1.promote()
        lara1.cap_stats()
        with self.assertRaises(ValueError):
            # (Still 'Thief Fighter')
            lara1.level_up(10)
            lara1.promote()

        # Thief
        lara2 = Morph5("Lara")
        with self.assertRaises(ValueError):
            lara2.promote()
        lara2.level_up(10)
        lara2.promo_cls = "Thief Fighter"
        # Thief Fighter
        lara2.promote()
        lara2.cap_stats()
        lara2.promo_cls = "Dancer"
        # Dancer
        lara2.promote()
        lara2.cap_stats()
        lara2.level_up(10)
        # Thief Fighter
        lara2.promote()
        with self.assertRaises(ValueError):
            # (Still 'Thief Fighter')
            lara2.level_up(10)
            lara2.promote()


class Morph7IntegrationTest(unittest.TestCase):
    """
    Runs through potential simulations of stat comparisons.
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


    def test_tutorial_wallace(self):
        """
        Tests that Tutorial!Wallace can be leveled-up, stat-capped, and promoted.
        """
        logging.warning("Morph7Test.test_tutorial_wallace()")
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
        logging.warning("Morph7Test.test_main_wallace()")
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
        logging.warning("Morph7Test.test_all_units()")
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


class Morph8IntegrationTest(unittest.TestCase):
    """
    Runs through potential simulations of stat comparisons.
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

class Morph9IntegrationTest(unittest.TestCase):
    """
    Runs through potential simulations of stat comparisons.
    """

    def setUp(self):
        """
        Creates a Morph object, with the option specified for full coverage.
        """
        self.ike = Morph9("Ike")
        self.assertFalse(any(self.ike.current_stats.isnull()))

    def test_all_units(self):
        """
        Performs a shallow test: each unit is put through a maxing journey.
        Assert: final > bases
        """
        logging.warning("Morph9Test.test_all_units()")
        ltable = "characters__base_stats"
        rtable = "classes__promotion_gains"
        with open(
                str(self.ike.home_dir.joinpath(f"{ltable}-JOIN-{rtable}.json")),
                encoding='utf-8') as rfile:
            promocls_dict = json.load(rfile)
        for unitname in self.ike.get_character_list():
            unit = Morph(9, unitname)
            bases = unit.current_stats.copy()
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
            self.assertTrue(any(unit.current_stats > bases))

if __name__ == '__main__':
    module = Morph5IntegrationTest
    findstr = "test_lara"
    unittest.main(
        defaultTest=[test for test in dir(module) if findstr in test],
        module=module,
    )
