"""
"""

import sqlite3
import unittest
from unittest.mock import patch
import enum
import logging

from aenir.games import FireEmblemGame
from aenir.morph import (
    BaseMorph,
    Morph,
    Morph4,
    Morph5,
    Morph6,
    Morph7,
    Morph8,
    Morph9,
)
from aenir.stats import (
    GenealogyStats,
    GBAStats,
    ThraciaStats,
    AbstractStats,
)

from aenir.logging import (
    configure_logging,
    logger,
    time_logger,
)

configure_logging()
time_logger.critical("")

class BaseMorphTests(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        logger.critical("%s", self.id())

        class TestMorph(BaseMorph):
            """
            """

        class TestMorph6(BaseMorph):
            """
            """
            @classmethod
            def GAME(cls):
                """
                """
                return FireEmblemGame(6)

        self.TestMorph = TestMorph
        self.TestMorph6 = TestMorph6

    def test_query_db__without_filters(self):
        """
        """
        path_to_db = "static/binding-blade/cleaned_stats.db"
        table = "characters__base_stats0"
        fields = ("HP", "Def")
        filters = None
        with sqlite3.connect(path_to_db) as cnxn:
            cnxn.row_factory = sqlite3.Row
            expected = cnxn.execute(
                "SELECT HP, Def FROM characters__base_stats0;",
            )
        actual = self.TestMorph.query_db(
            path_to_db,
            table,
            fields,
            filters,
        )
        self.assertEqual(actual.fetchall(), expected.fetchall())

    def test_query_db__with_filters(self):
        """
        """
        path_to_db = "static/binding-blade/cleaned_stats.db"
        table = "characters__base_stats0"
        fields = ("Pow", "Spd")
        filters = {"Name": "Rutger"}
        with sqlite3.connect(path_to_db) as cnxn:
            cnxn.row_factory = sqlite3.Row
            expected = cnxn.execute(
                "SELECT Pow, Spd FROM characters__base_stats0 WHERE Name='Rutger';",
            )
        actual = self.TestMorph.query_db(
            path_to_db,
            table,
            fields,
            filters,
        )
        self.assertEqual(actual.fetchall(), expected.fetchall())

    def test_query_db__with_filters__no_results(self):
        """
        """
        path_to_db = "static/binding-blade/cleaned_stats.db"
        table = "characters__base_stats0"
        fields = ("Pow", "Spd")
        filters = {"Name": "Ruter"}
        with sqlite3.connect(path_to_db) as cnxn:
            cnxn.row_factory = sqlite3.Row
            expected = cnxn.execute(
                "SELECT Pow, Spd FROM characters__base_stats0 WHERE false;",
            )
        actual = self.TestMorph.query_db(
            path_to_db,
            table,
            fields,
            filters,
        )
        self.assertEqual(actual.fetchall(), expected.fetchall())

    def test_query_db__fields_not_iterable(self):
        """
        """
        path_to_db = "static/binding-blade/cleaned_stats.db"
        table = "characters__base_stats0"
        fields = None
        filters = {"Name": "Ruter"}
        with self.assertRaises(TypeError):
            self.TestMorph.query_db(
                path_to_db,
                table,
                fields,
                filters,
            )

    def test_query_db__filterset_has_no_items_method(self):
        """
        """
        path_to_db = "static/binding-blade/cleaned_stats.db"
        table = "characters__base_stats0"
        fields = ("Pow", "Spd")
        filters = [("Name", "Rutger")]
        with self.assertRaises(AttributeError):
            self.TestMorph.query_db(
                path_to_db,
                table,
                fields,
                filters,
            )

    def test_query_db__path_not_str(self):
        """
        """
        path_to_db = None
        table = "characters__base_stats0"
        fields = ("Pow", "Spd")
        filters = {"Name": "Ruter"}
        with self.assertRaises(TypeError):
            self.TestMorph.query_db(
                path_to_db,
                table,
                fields,
                filters,
            )

    def test_query_db__table_dne(self):
        """
        """
        path_to_db = "static/binding-blade/cleaned_stats.db"
        table = "characters__base_stats"
        fields = ("Pow", "Spd")
        filters = {"Name": "Ruter"}
        with self.assertRaises(sqlite3.OperationalError):
            self.TestMorph.query_db(
                path_to_db,
                table,
                fields,
                filters,
            )

    def test_GAME(self):
        """
        """
        with self.assertRaises(NotImplementedError):
            self.TestMorph.GAME()

    def test_STATS(self):
        """
        """
        gameno_to_stats = {
            4: GenealogyStats,
            5: ThraciaStats,
            6: GBAStats,
            7: GBAStats,
            8: GBAStats,
            9: GenealogyStats,
        }
        for game_no, stats in gameno_to_stats.items():
            class TestMorphWithGame(BaseMorph):
                """
                """
                @classmethod
                def GAME(cls):
                    """
                    """
                    return FireEmblemGame(game_no)
            expected = gameno_to_stats[game_no]
            actual = TestMorphWithGame.STATS()
            self.assertEqual(actual, expected)

    def test_path_to__GAME_not_implemented(self):
        """
        """
        with self.assertRaises(NotImplementedError):
            self.TestMorph.path_to("something")

    def test_path_to__no_url_name_attribute(self):
        """
        """
        class TestMorphNoURLName(BaseMorph):
            """
            """
            @classmethod
            def GAME(cls):
                """
                """
                return 4
        with self.assertRaises(AttributeError):
            self.TestMorphNoURLName.path_to("something")

    def test_path_to__file_is_not_string(self):
        """
        """
        with self.assertRaises(TypeError):
            self.TestMorph6.path_to(None)

    def test_lookup(self):
        """
        """
        home_data = ("characters__base_stats", "Roy")
        target_data = ("classes__maximum_stats", "Class")
        tableindex = 0
        morph6 = self.TestMorph6()
        actual = morph6.lookup(
            home_data,
            target_data,
            tableindex,
        )
        expected = {
            "path_to_db": "static/binding-blade/cleaned_stats.db",
            "table": "classes__maximum_stats0",
            "fields": ("HP", "Pow", "Skl", "Spd", "Lck", "Def", "Res"),
            "filters": {"Class": "Non-promoted"},
        }
        self.assertDictEqual(actual, expected)
        # resultset is not None (check if 'query_db' is called)

    def test_lookup__bad_data_passed(self):
        """
        """
        home_data = ("characters__base_stats", "Roy", None)
        target_data = ("classes__maximum_stats", "Class")
        tableindex = 0
        morph6 = self.TestMorph6()
        with self.assertRaises(ValueError):
            morph6.lookup(
                home_data,
                target_data,
                tableindex,
            )

    def test_lookup__json_file_dne(self):
        """
        """
        # JSON file does not exist
        home_data = ("characters__base_stats", "Roy")
        target_data = ("classes__maximum_stat", "Class")
        tableindex = 0
        morph6 = self.TestMorph6()
        with self.assertRaises(FileNotFoundError):
            morph6.lookup(
                home_data,
                target_data,
                tableindex,
            )

    @patch("json.load")
    def test_lookup__aliased_value_is_none(self, MOCK_json_load):
        """
        """
        home_data = ("characters__base_stats", "Roy")
        target_data = ("classes__maximum_stats", "Class")
        tableindex = 0
        morph6 = self.TestMorph6()
        MOCK_json_load.return_value = {"Roy": None}
        actual = morph6.lookup(
            home_data,
            target_data,
            tableindex,
        )
        self.assertIsNone(actual)
        # resultset is None

    def test_lookup__lookup_value_dne(self):
        """
        """
        # JSON file does not exist
        home_data = ("characters__base_stats", "Marth")
        target_data = ("classes__maximum_stats", "Class")
        tableindex = 0
        morph6 = self.TestMorph6()
        with self.assertRaises(KeyError):
            morph6.lookup(
                home_data,
                target_data,
                tableindex,
            )
        # lookup value not found

    def test_query_db__more_than_one_filter_provided(self):
        """
        """
        path_to_db = "static/binding-blade/cleaned_stats.db"
        table = "characters__growth_rates0"
        fields = ("Pow", "Spd")
        filters = {"Spd": 40, "Pow": 40}
        # should return Wendy, Wolt, and Roy.
        with sqlite3.connect(path_to_db) as cnxn:
            cnxn.row_factory = sqlite3.Row
            expected = cnxn.execute(
                'SELECT Pow, Spd FROM characters__growth_rates0 WHERE Spd=40 AND Pow=40;',
            )
        actual = self.TestMorph.query_db(
            path_to_db,
            table,
            fields,
            filters,
        )
        #self.assertTrue(expected.fetchall())
        expected_resultset = expected.fetchall()
        actual_resultset = actual.fetchall()
        self.assertTrue(expected_resultset)
        self.assertEqual(actual_resultset, expected_resultset)

class MorphTests(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        logger.critical("%s", self.id())
        class TestMorph6(Morph):
            """
            """
            #__name__ = "Morph"
            game_no = 6

        self.TestMorph = TestMorph6
        self.TestMorph.__name__ = "Morph"
        self.init_kwargs = {
            "name": "Rutger",
            "which_bases": 0,
            "which_growths": 0,
        }

    def test_GAME(self):
        """
        """
        with self.assertLogs(logger, logging.WARNING):
            self.TestMorph.GAME()

    def test_CHARACTER_LIST(self):
        """
        """
        expected = [
            "Roy",
            "Marcus",
            "Allen",
            "Lance",
            "Wolt",
            "Bors",
            "Merlinus",
            "Ellen",
            "Dieck",
            "Wade",
            "Lott",
            "Thany",
            "Chad",
            "Lugh",
            "Clarine",
            "Rutger",
            "Rutger (HM)",
            "Saul",
            "Dorothy",
            "Sue",
            "Zealot",
            "Treck",
            "Noah",
            "Astohl",
            "Lilina",
            "Wendy",
            "Barth",
            "Oujay",
            "Fir",
            "Fir (HM)",
            "Shin",
            "Shin (HM)",
            "Gonzales",
            "Gonzales (HM)",
            "Geese",
            "Klein",
            "Klein (HM)",
            "Tate",
            "Tate (HM)",
            "Lalum",
            "Echidna",
            "Elphin",
            "Bartre",
            "Ray",
            "Cath",
            "Cath (HM)",
            "Miredy",
            "Miredy (HM)",
            "Percival",
            "Percival (HM)",
            "Cecilia",
            "Sofiya",
            "Igrene",
            "Garret",
            "Garret (HM)",
            "Fa",
            "Hugh",
            "Zeis",
            "Zeis (HM)",
            "Douglas",
            "Niime",
            "Dayan",
            "Juno",
            "Yodel",
            "Karel",
            "Narshen",
            "Gale",
            "Hector",
            "Brunya",
            "Eliwood",
            "Murdoch",
            "Zephiel",
            "Guinevere",
        ]
        actual = self.TestMorph.CHARACTER_LIST()
        self.assertListEqual(actual, expected)

    def test_init(self):
        """
        """
        rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        # test for attribute-value pairs
        self.assertEqual(rutger.name, "Rutger")
        self.assertEqual(rutger.game, FireEmblemGame(6))
        self.assertEqual(rutger.Stats, GBAStats)
        self.assertEqual(rutger.current_cls, "Myrmidon")
        self.assertEqual(rutger.current_lv, 4)
        self.assertEqual(
            rutger.current_stats,
            GBAStats(
                HP=22,
                Pow=7,
                Skl=12,
                Spd=13,
                Lck=2,
                Def=5,
                Res=0,
            ),
        )
        self.assertEqual(
            rutger.growth_rates,
            GBAStats(
                HP=80,
                Pow=30,
                Skl=60,
                Spd=50,
                Lck=30,
                Def=20,
                Res=20,
            ),
        )
        self.assertEqual(
            rutger.max_stats,
            GBAStats(
                HP=60,
                Pow=20,
                Skl=20,
                Spd=20,
                Lck=30,
                Def=20,
                Res=20,
            )
        )
        self.assertDictEqual(
            rutger._meta,
            {
                "History": [],
                "Hard Mode": False,
                "Stat Boosters": [],
            },
        )

    def test_init__unit_dne(self):
        """
        """
        with self.assertRaises(ValueError) as assert_ctx:
            marth = self.TestMorph("Marth", which_bases=0, which_growths=0)
        (err_msg,) = assert_ctx.exception.args
        self.assertIn("%r" % list(self.TestMorph.CHARACTER_LIST()), err_msg)

    def test_init__bad_bases_index(self):
        """
        """
        bad_bases = 99
        with self.assertRaises(sqlite3.OperationalError):
            roy = self.TestMorph("Roy", which_bases=bad_bases, which_growths=0)

    def test_init__bad_growths_index(self):
        """
        """
        bad_growths = 99
        with self.assertRaises(sqlite3.OperationalError):
            roy = self.TestMorph("Roy", which_bases=0, which_growths=bad_growths)

    def test_set_max_level(self):
        """
        """
        morph = self.TestMorph(**self.init_kwargs)
        self.assertIsNone(morph.max_level)
        morph._set_max_level()
        self.assertIsInstance(morph.max_level, int)

    def test_set_min_promo_level(self):
        """
        """
        morph = self.TestMorph(**self.init_kwargs)
        self.assertIsNone(morph.min_promo_level)
        morph._set_min_promo_level()
        self.assertIsInstance(morph.min_promo_level, int)

    def test_level_up(self):
        """
        """
        rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        rutger.level_up(16)
        self.assertEqual(rutger.current_lv, 20)
        expected = True
        actual = all(
            rutger.current_stats == \
            GBAStats(
                HP=34.8,
                Pow=11.8,
                Skl=20,
                Spd=20,
                Lck=6.8,
                Def=8.2,
                Res=3.2,
            )
        )
        self.assertIs(actual, expected)

    def test_level_up__level_too_high(self):
        """
        """
        rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        with self.assertRaises(ValueError):
            rutger.level_up(20)
        base_rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        self.assertEqual(rutger.current_lv, base_rutger.current_lv)
        expected = True
        actual = all(
            rutger.current_stats == base_rutger.current_stats,
        )
        self.assertIs(actual, expected)

    def test_promote(self):
        """
        """
        rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        rutger.min_promo_level = 0
        rutger.promote()
        self.assertListEqual(
            rutger._meta["History"],
            [(4, "Myrmidon")],
        )
        self.assertEqual(rutger.current_clstype, "classes__promotion_gains")
        self.assertEqual(rutger.current_cls, "Swordmaster (M)")
        self.assertEqual(rutger.current_lv, 1)
        self.assertIsNone(rutger.promo_cls)
        # assert maxes are those of Swordmaster
        swordmaster_maxes = GBAStats(
            HP=60,
            Pow=24,
            Skl=29,
            Spd=30,
            Lck=30,
            Def=22,
            Res=23,
        )
        actual = all(swordmaster_maxes == rutger.max_stats)
        self.assertIs(actual, True)
        # assert that stats have increased by expected amount.
        base_rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        promo_bonuses = GBAStats(
            HP=5,
            Pow=2,
            Skl=2,
            Spd=1,
            Lck=0,
            Def=3,
            Res=2,
        )
        actual2 = all(
            base_rutger.current_stats + promo_bonuses == rutger.current_stats
        )
        self.assertIs(actual2, True)

    def test_promote__level_too_low(self):
        """
        """
        rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        with self.assertRaises(ValueError):
            rutger.promote()
        self.assertListEqual(
            rutger._meta["History"],
            [],
        )
        self.assertEqual(rutger.current_clstype, "characters__base_stats")
        self.assertEqual(rutger.current_cls, "Myrmidon")
        self.assertEqual(rutger.current_lv, 4)
        #self.assertIsNone(rutger.promo_cls)
        # assert maxes are those of Swordmaster
        unpromoted_maxes = GBAStats(
            HP=60,
            Pow=20,
            Skl=20,
            Spd=20,
            Lck=30,
            Def=20,
            Res=20,
        )
        actual = all(unpromoted_maxes == rutger.max_stats)
        self.assertIs(actual, True)
        # assert that stats have not increased by expected amount.
        base_rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        actual2 = all(
            base_rutger.current_stats == rutger.current_stats
        )
        self.assertIs(actual2, True)

    def test_promote__already_promoted(self):
        """
        """
        rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        rutger.name = "Marcus"
        with self.assertRaises(ValueError):
            rutger.promote()
        self.assertListEqual(
            rutger._meta["History"],
            [],
        )
        self.assertEqual(rutger.current_clstype, "characters__base_stats")
        self.assertEqual(rutger.current_cls, "Myrmidon")
        self.assertEqual(rutger.current_lv, 4)
        #self.assertIsNone(rutger.promo_cls)
        # assert maxes are those of Swordmaster
        unpromoted_maxes = GBAStats(
            HP=60,
            Pow=20,
            Skl=20,
            Spd=20,
            Lck=30,
            Def=20,
            Res=20,
        )
        actual = all(unpromoted_maxes == rutger.max_stats)
        self.assertIs(actual, True)
        # assert that stats have not increased by expected amount.
        base_rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        actual2 = all(
            base_rutger.current_stats == rutger.current_stats
        )
        self.assertIs(actual2, True)

    def test_promote__branched_promotion(self):
        """
        """
        class TestMorph4(Morph):
            """
            """
            #__name__ = "Morph"
            game_no = 4
            @classmethod
            def GAME(cls):
                """
                """
                return FireEmblemGame(cls.game_no)
        ira = TestMorph4("Ira", which_bases=0, which_growths=0)
        ira.current_lv = 10
        ira.promo_cls = "Swordmaster"
        ira.promote()
        self.assertListEqual(
            ira._meta["History"],
            [(10, "Swordfighter")],
        )
        self.assertEqual(ira.current_clstype, "classes__promotion_gains")
        self.assertEqual(ira.current_cls, "Swordmaster")
        # to be amended in the Morph4 subclass
        #self.assertEqual(ira.current_lv, 1)
        self.assertIsNone(ira.promo_cls)
        # assert maxes are those of Swordmaster
        swordmaster_maxes = GenealogyStats(
            HP=80,
            Str=27,
            Mag=15,
            Skl=30,
            Spd=30,
            Lck=30,
            Def=22,
            Res=18,
        )
        actual = all(swordmaster_maxes == ira.max_stats)
        self.assertIs(actual, True)
        # assert that stats have increased by expected amount.
        base_ira = TestMorph4("Ira", which_bases=0, which_growths=0)
        promo_bonuses = GenealogyStats(
            HP=0,
            Str=5,
            Mag=0,
            Skl=5,
            Spd=5,
            Lck=0,
            Def=2,
            Res=3,
        )
        actual2 = all(
            base_ira.current_stats + promo_bonuses == ira.current_stats
        )
        self.assertIs(actual2, True)

    def test_promote__branched_promotion_again(self):
        """
        """
        class TestMorph4(Morph):
            """
            """
            #__name__ = "Morph"
            game_no = 4
            @classmethod
            def GAME(cls):
                """
                """
                return FireEmblemGame(cls.game_no)
        holyn = TestMorph4("Holyn", which_bases=0, which_growths=0)
        holyn.current_lv = 10
        holyn.promo_cls = "Forrest"
        holyn.promote()
        self.assertListEqual(
            holyn._meta["History"],
            [(10, "Swordfighter")],
        )
        self.assertEqual(holyn.current_clstype, "classes__promotion_gains")
        self.assertEqual(holyn.current_cls, "Forrest")
        # to be amended in the Morph4 subclass
        #self.assertEqual(holyn.current_lv, 1)
        self.assertIsNone(holyn.promo_cls)
        # assert maxes are those of Swordmaster
        swordmaster_maxes = GenealogyStats(
            HP=80,
            Str=27,
            Mag=18,
            Skl=27,
            Spd=27,
            Lck=30,
            Def=22,
            Res=18,
        )
        actual = all(swordmaster_maxes == holyn.max_stats)
        self.assertIs(actual, True)
        # assert that stats have increased by expected amount.
        base_holyn = TestMorph4("Holyn", which_bases=0, which_growths=0)
        promo_bonuses = GenealogyStats(
            HP=0,
            Str=5,
            Mag=3,
            Skl=2,
            Spd=2,
            Lck=0,
            Def=2,
            Res=3,
        )
        actual2 = all(
            base_holyn.current_stats + promo_bonuses == holyn.current_stats
        )
        self.assertIs(actual2, True)

    def test_use_stat_booster(self):
        """
        """
        roy = self.TestMorph("Roy", which_bases=0, which_growths=0)
        item_bonus_dict = {
            "Angelic Robe": ("HP", 7),
            "Energy Ring": ("Pow", 2),
            "Secret Book": ("Skl", 2),
            "Speedwings": ("Spd", 2),
            "Goddess Icon": ("Lck", 2),
            "Dragonshield": ("Def", 2),
            "Talisman": ("Res", 2),
            #"Boots": ("Mov", 2),
            #"Body Ring": ("Con", 3),
        }
        expected = roy.current_stats.as_dict()
        for stat, bonus in item_bonus_dict.values():
            expected[stat] += bonus
        for item in item_bonus_dict:
            roy.use_stat_booster(item, item_bonus_dict)
        actual = roy.current_stats.as_dict()
        self.assertDictEqual(actual, expected)

    def test_use_stat_booster__fail(self):
        """
        """
        roy = self.TestMorph("Roy", which_bases=0, which_growths=0)
        item_bonus_dict = {
            "Angelic Robe": ("HP", 7),
            "Energy Ring": ("Pow", 2),
            "Secret Book": ("Skl", 2),
            "Speedwings": ("Spd", 2),
            "Goddess Icon": ("Lck", 2),
            "Dragonshield": ("Def", 2),
            "Talisman": ("Res", 2),
            #"Boots": ("Mov", 2),
            #"Body Ring": ("Con", 3),
        }
        with self.assertRaises(KeyError):
            item = ""
            roy.use_stat_booster(item, item_bonus_dict)

    def test_promote__branch_unspecified(self):
        """
        """
        class Morph8(Morph):
            """
            """
            game_no = 8
        ross = Morph8("Ross", which_bases=0, which_growths=0)
        ross.current_lv = 10
        valid_promotions = ['Fighter', 'Pirate', 'Journeyman (2)']
        with self.assertRaises(KeyError) as key_ctx:
            ross.promote()
        (err_msg,) = key_ctx.exception.args
        self.assertIn(str(valid_promotions), err_msg)

    @unittest.skip("Not implemented yet.")
    def test_repr(self):
        """
        """
        # NOTE: for CLI only. low priority

    @unittest.skip("Not implemented yet.")
    def test_lt(self):
        """
        """
        # NOTE: for CLI only. low priority

class Morph4Tests(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        logger.critical("%s", self.id())

    @staticmethod
    def _get_unit_list(can_promote=None):
        """
        """
        # query for list of units who cannot promote
        path_to_json = "static/genealogy-of-the-holy-war/characters__base_stats-JOIN-classes__promotion_gains.json"
        with open(path_to_json) as rfile:
            promo_dict = json.read(rfile)
        return list(
            map(
                lambda item: item[0],
                filter(
                    {
                        False: lambda item: item[1] is not None,
                        True: lambda item: item[1] is None,
                        None: lambda item: True,
                    }[can_promote], promo_dict,
                )
            )
        )

    @staticmethod
    def _get_kid_list():
        """
        """
        # query for list of kids
        path_to_db = "static/genealogy-of-the-holy-war/cleaned_stats.db"
        with sqlite3.connect(path_to_db) as cnxn:
            resultset = [result["Name"] for result in cnxn.execute("SELECT Name FROM characters__base_stats1;").fetchall()]
        kid_list = sorted(set(resultset), key=lambda name: resultset.index(name))
        return kid_list

    @staticmethod
    def _get_father_list():
        """
        """
        # query for list of fathers
        path_to_db = "static/genealogy-of-the-holy-war/cleaned_stats.db"
        with sqlite3.connect(path_to_db) as cnxn:
            resultset = [result["Father"] for result in cnxn.execute("SELECT Father FROM characters__base_stats1;").fetchall()]
        father_list = sorted(set(resultset), key=lambda name: resultset.index(name))
        return father_list

    def test_sigurd(self):
        """
        """
        sigurd = Morph4("Sigurd")
        self.assertEqual(sigurd.current_lv, 5)
        sigurd.level_up(15)
        with self.assertRaises(ValueError):
            sigurd.promote()
        sigurd.level_up(10)
        with self.assertRaises(ValueError):
            sigurd.level_up(1)

    def test_ira(self):
        """
        """
        ira = Morph4("Ira")
        self.assertEqual(ira.current_lv, 4)
        with self.assertRaises(ValueError):
            ira.promote()
        ira.level_up(16)
        ira.promote()
        ira.level_up(10)
        self.assertEqual(ira.current_lv, 30)
        with self.assertRaises(ValueError):
            ira.level_up(1)

    def test_arden(self):
        """
        """
        arden = Morph4("Arden")
        self.assertEqual(arden.current_lv, 3)
        with self.assertRaises(ValueError):
            arden.promote()
        arden.level_up(17)
        arden.promote()
        with self.assertRaises(ValueError):
            arden.promote()
        arden.level_up(10)
        with self.assertRaises(ValueError):
            arden.level_up(1)

    def test_lakche_with_father_lex(self):
        """
        """
        lakche = Morph4("Lakche", father="Lex")
        self.assertEqual(lakche.current_lv, 1)
        with self.assertRaises(ValueError):
            lakche.promote()
        lakche.level_up(19)
        lakche.promote()
        lakche.level_up(10)
        with self.assertRaises(ValueError):
            lakche.level_up(1)

    def test_lakche_as_bastard(self):
        """
        """
        with self.assertRaises(KeyError) as key_ctx:
            Morph4("Lakche", father="")
        # generate father list
        path_to_db = Morph4.path_to("cleaned_stats.db")
        table = "characters__base_stats1"
        fields = ["Father"]
        filters = None
        logger.debug("Morph4.query_db('%s', '%s', %r, %r)",
            path_to_db,
            table,
            fields,
            filters,
        )
        resultset = Morph4.query_db(
            path_to_db,
            table,
            fields,
            filters,
        ).fetchall()
        # check that father list is inside error message.
        father_list = [result["Father"] for result in resultset]
        father_list = sorted(set(father_list), key=lambda name: father_list.index(name))
        (err_msg,) = key_ctx.exception.args
        self.assertIn("%r" % father_list, err_msg)
        logger.debug("%s", father_list)

    # TODO: This.

    def test_nonkids_who_can_promote(self):
        """
        """

    def test_nonkids_who_cannot_promote(self):
        """
        """

    def test_kids_who_can_promote(self):
        """
        """

    def test_kids_who_cannot_promote(self):
        """
        """

