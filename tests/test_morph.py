#!/usr/bin/python3
"""
"""

import sqlite3
import logging
import json
import unittest
from unittest.mock import patch

from aenir.games import FireEmblemGame
from aenir.morph import (
    get_morph,
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
    RadiantStats,
)
from aenir._exceptions import (
    UnitNotFoundError,
    LevelUpError,
    PromotionError,
    StatBoosterError,
    ScrollError,
    BandError,
    GrowthsItemError,
    KnightWardError,
    InitError,
)

from aenir._logging import (
    configure_logging,
    logger,
    time_logger,
)

configure_logging()
time_logger.critical("")


def _get_promotables(url_name, can_promote):
    """
    """
    # query for list of units who cannot promote
    table_name = "characters__base_stats-JOIN-classes__promotion_gains"
    path_to_db = f"static/{url_name}/cleaned_stats.db"
    with sqlite3.connect(path_to_db) as cnxn:
        cnxn.row_factory = sqlite3.Row
        resultset = cnxn.execute(f"SELECT Name, Alias FROM '{table_name}';")
        promo_dict = dict(resultset)
    #logger.debug("%s", promo_dict)
    return list(
        map(
            lambda item: item[0],
            filter(
                {
                    True: lambda item: item[1] is not None,
                    False: lambda item: item[1] is None,
                }[can_promote], promo_dict.items(),
            )
        )
    )

class BaseMorphTests(unittest.TestCase):
    """
    """

    def tearDown(self):
        """
        """
        logger.critical("%s", self.id())

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
            9: RadiantStats,
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
            def GAME():
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
            "fields": ("HP", "Pow", "Skl", "Spd", "Lck", "Def", "Res", "Con", "Mov"),
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
        with self.assertRaises(sqlite3.OperationalError):
            morph6.lookup(
                home_data,
                target_data,
                tableindex,
            )

    @patch("sqlite3.Cursor.fetchone")
    def test_lookup__aliased_value_is_none(self, MOCK_fetchone):
        """
        """
        home_data = ("characters__base_stats", "Roy")
        target_data = ("classes__maximum_stats", "Class")
        tableindex = 0
        morph6 = self.TestMorph6()
        MOCK_fetchone.return_value = {"Roy": None}
        actual = morph6.lookup(
            home_data,
            target_data,
            tableindex,
        )
        self.assertIsNone(actual)
        # resultset is None

    @unittest.skip
    #@patch("json.load")
    #def test_lookup__aliased_value_is_none(self, MOCK_json_load):
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

    @unittest.skip
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

    def test_lookup__lookup_value_dne(self):
        """
        """
        # JSON file does not exist
        home_data = ("characters__base_stats", "Marth")
        target_data = ("classes__maximum_stats", "Class")
        tableindex = 0
        morph6 = self.TestMorph6()
        actual = morph6.lookup(
            home_data,
            target_data,
            tableindex,
        )
        self.assertIsNone(actual)
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

    def tearDown(self):
        """
        """
        logger.critical("%s", self.id())

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

    def test_as_string(self):
        """
        """
        morph = self.TestMorph(**self.init_kwargs)
        morph.use_stat_booster("Angelic Robe", {"Angelic Robe": ("HP", 7)})
        miscellany = [("Hard Mode", "True")]
        actual = morph.as_string(miscellany=miscellany, show_stat_boosters=True)
        logger.debug("as_string -> %s", actual)

    def test_inventory_size_is_zero(self):
        """
        """
        morph = self.TestMorph(**self.init_kwargs)
        actual = morph.inventory_size
        expected = 0
        self.assertEqual(actual, expected)

    def test_iter(self):
        """
        """
        kwargs = self.init_kwargs
        morph = self.TestMorph(**kwargs)
        _expected = [
            ("HP", 22),
            ("Pow", 7),
            ("Skl", 12),
            ("Spd", 13),
            ("Lck", 2),
            ("Def", 5),
            ("Res", 0),
            #("Con", 7),
            #("Mov", 5),
        ]
        #self.assertEqual(len(morph), expected)
        actual = []
        for statval in morph:
            actual.append(statval)
        expected = [numval for (_, numval) in _expected]
        self.assertListEqual(actual, expected)

    def test_get_true_character_list5(self):
        """
        """
        class Morph5(Morph):
            """
            """
            game_no = 5
        expected = Morph5.CHARACTER_LIST()
        actual = Morph5.get_true_character_list()
        self.assertEqual(tuple(actual), expected)

    @unittest.skip("Removed the logging call from this method.")
    def test_GAME(self):
        """
        """
        with self.assertLogs(logger, logging.WARNING):
            self.TestMorph.GAME()

    def test_CHARACTER_LIST(self):
        """
        """
        expected = (
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
        )
        actual = self.TestMorph.CHARACTER_LIST()
        self.assertTupleEqual(actual, expected)

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
        actual = rutger.current_stats
        expected = GBAStats(
            HP=22,
            Pow=7,
            Skl=12,
            Spd=13,
            Lck=2,
            Def=5,
            Res=0,
            Con=7,
            Mov=5,
        )
        self.assertEqual(
            actual, expected,
        )
        actual = rutger.growth_rates
        expected = GBAStats(
            HP=80,
            Pow=30,
            Skl=60,
            Spd=50,
            Lck=30,
            Def=20,
            Res=20,
            Con=0,
            Mov=0,
        )
        self.assertEqual(
            actual, expected,
        )
        actual = rutger.max_stats
        expected = GBAStats(
            HP=60,
            Pow=20,
            Skl=20,
            Spd=20,
            Lck=30,
            Def=20,
            Res=20,
            Con=20,
            Mov=15,
        )
        self.assertEqual(
            actual,
            expected,
        )
        actual = rutger._meta
        expected = {
            "Hard Mode": False,
            "Stat Boosters": [],
        }
        self.assertDictEqual(
            actual, expected,
        )

    def test_init__unit_dne(self):
        """
        """
        with self.assertRaises(UnitNotFoundError) as assert_ctx:
            marth = self.TestMorph("Marth", which_bases=0, which_growths=0)
        (err_msg,) = assert_ctx.exception.args
        self.assertIn("%r" % (tuple(self.TestMorph.CHARACTER_LIST()),), err_msg)
        actual = assert_ctx.exception.unit_type
        expected = UnitNotFoundError.UnitType.NORMAL
        self.assertEqual(actual, expected)

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
        actual = rutger.current_stats
        expected = GBAStats(
            HP=34.8,
            Pow=11.8,
            Skl=20,
            Spd=20,
            Lck=6.8,
            Def=8.2,
            Res=3.2,
            Con=7,
            Mov=5,
        )
        self.assertEqual(actual, expected)

    def test_level_up__level_too_high(self):
        """
        """
        rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        with self.assertRaises(LevelUpError):
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
            rutger.history,
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
            Con=20,
            Mov=15,
        )
        expected = swordmaster_maxes
        actual = rutger.max_stats
        self.assertEqual(actual, expected)
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
            Con=1,
            Mov=1,
        )
        actual = rutger.current_stats
        expected = (base_rutger.current_stats + promo_bonuses)
        self.assertEqual(actual, expected)

    def test_stat_comparison_fail(self):
        """
        """
        rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        rutger.current_stats.Mov = 99 # This is what will cause the test to fail
        actual = rutger.current_stats
        expected = GBAStats(
            HP=22,
            Pow=7,
            Skl=12,
            Spd=13,
            Lck=2,
            Def=5,
            Res=0,
            Con=7,
            Mov=5,
        )
        actual_eq_expected = actual == expected
        with self.assertRaises(AssertionError):
            self.assertIs(
                actual_eq_expected, True,
            )

    def test_promote__level_too_low(self):
        """
        """
        rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        with self.assertRaises(PromotionError) as exc_ctx:
            rutger.promote()
        actual = exc_ctx.exception.reason
        expected = PromotionError.Reason.LEVEL_TOO_LOW
        self.assertEqual(actual, expected)
        self.assertListEqual(
            rutger.history,
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
            Con=20,
            Mov=15,
        )
        expected = unpromoted_maxes
        actual = rutger.max_stats
        self.assertEqual(actual, expected)
        # assert that stats have not increased by expected amount.
        base_rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        expected = base_rutger.current_stats
        actual = rutger.current_stats
        self.assertEqual(actual, expected)

    def test_promote__already_promoted(self):
        """
        """
        rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        rutger.name = "Marcus"
        with self.assertRaises(PromotionError) as exc_ctx:
            rutger.promote()
        actual = exc_ctx.exception.reason
        expected = PromotionError.Reason.NO_PROMOTIONS
        self.assertEqual(actual, expected)
        self.assertListEqual(
            rutger.history,
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
            Con=20,
            Mov=15,
        )
        expected = unpromoted_maxes
        actual = rutger.max_stats
        self.assertEqual(actual, expected)
        # assert that stats have not increased by expected amount.
        base_rutger = self.TestMorph("Rutger", which_bases=0, which_growths=0)
        expected = base_rutger.current_stats
        actual = rutger.current_stats
        self.assertEqual(actual, expected)

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
            ira.history,
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
            #Con=20,
            #Mov=15,
        )
        expected = swordmaster_maxes
        actual = ira.max_stats
        self.assertEqual(actual, expected)
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
        expected = base_ira.current_stats + promo_bonuses
        actual = ira.current_stats
        self.assertEqual(actual, expected)

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
            holyn.history,
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
        expected = swordmaster_maxes
        actual = holyn.max_stats
        self.assertEqual(actual, expected)
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
        expected = (base_holyn.current_stats + promo_bonuses)
        actual = holyn.current_stats
        self.assertEqual(actual, expected)

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
            "Boots": ("Mov", 2),
            "Body Ring": ("Con", 3),
        }
        expected = roy.current_stats.as_dict()
        for stat, bonus in item_bonus_dict.values():
            expected[stat] += bonus
        roy.stat_boosters = item_bonus_dict
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
            "Boots": ("Mov", 2),
            "Body Ring": ("Con", 3),
        }
        item = ""
        roy.stat_boosters = item_bonus_dict
        with self.assertRaises(StatBoosterError) as err_ctx:
            roy.use_stat_booster(item, item_bonus_dict)
        actual = err_ctx.exception.reason
        expected = StatBoosterError.Reason.NOT_FOUND
        self.assertEqual(actual, expected)

    def test_promote__branch_unspecified(self):
        """
        """
        class Morph8(Morph):
            """
            """
            game_no = 8
        ross = Morph8("Ross", which_bases=0, which_growths=0)
        ross.current_lv = 10
        valid_promotions = ('Fighter', 'Pirate', 'Journeyman (2)')
        with self.assertRaises(PromotionError) as err_ctx:
            ross.promote()
        (err_msg,) = err_ctx.exception.args
        self.assertIn(str(valid_promotions), err_msg)
        actual = err_ctx.exception.reason
        expected = PromotionError.Reason.INVALID_PROMOTION
        self.assertEqual(actual, expected)

class Morph4Tests(unittest.TestCase):
    """
    """

    def tearDown(self):
        """
        """
        logger.critical("%s", self.id())

    def setUp(self):
        """
        """
        logger.critical("%s", self.id())

    @staticmethod
    def _get_promotables(can_promote):
        """
        """
        # query for list of units who cannot promote
        url_name = "genealogy-of-the-holy-war"
        return _get_promotables(url_name, can_promote=can_promote)

    def test_init__father_specified_for_nonkid(self):
        """
        """
        with self.assertLogs(logger, logging.WARNING):
            Morph4("Sigurd", father="Sigurd")

    def test_get_promotion_item__promoted(self):
        """
        """
        morph = Morph4("Sigurd")
        self.assertEqual(morph.max_level, 30)
        #with self.assertRaises(ValueError):
        actual = morph.get_promotion_item()
        self.assertIsNone(actual)

    def test_get_promotion_item__deirdre(self):
        """
        """
        morph = Morph4("Diadora")
        self.assertEqual(morph.max_level, 30)
        #with self.assertRaises(ValueError):
        actual = morph.get_promotion_item()
        self.assertIsNone(actual)

    def test_get_promotion_item__unpromoted(self):
        """
        """
        morph = Morph4("Lex")
        actual = morph.get_promotion_item()
        expected = "*Promote at Base*"
        self.assertEqual(actual, expected)

    def test_inventory_size(self):
        """
        """
        morph = Morph4("Sigurd")
        actual = morph.inventory_size
        self.assertIsInstance(actual, int)
        self.assertGreater(actual, 0)

    @staticmethod
    def _get_kid_list():
        """
        """
        # query for list of kids
        path_to_db = "static/genealogy-of-the-holy-war/cleaned_stats.db"
        with sqlite3.connect(path_to_db) as cnxn:
            cnxn.row_factory = sqlite3.Row
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
            cnxn.row_factory = sqlite3.Row
            resultset = [result["Father"] for result in cnxn.execute("SELECT Father FROM characters__base_stats1;").fetchall()]
        father_list = sorted(set(resultset), key=lambda name: resultset.index(name))
        return father_list

    def test_sigurd(self):
        """
        """
        sigurd = Morph4("Sigurd")
        self.assertEqual(sigurd.current_lv, 5)
        sigurd.level_up(15)
        with self.assertRaises(PromotionError) as err_ctx:
            sigurd.promote()
        expected = err_ctx.exception.reason
        actual = PromotionError.Reason.NO_PROMOTIONS
        self.assertEqual(actual, expected)
        sigurd.level_up(10)
        with self.assertRaises(LevelUpError):
            sigurd.level_up(1)

    def test_ira(self):
        """
        """
        ira = Morph4("Ira")
        self.assertEqual(ira.current_lv, 4)
        with self.assertRaises(PromotionError) as exc_ctx:
            ira.promote()
        actual = exc_ctx.exception.reason
        expected = PromotionError.Reason.LEVEL_TOO_LOW
        self.assertEqual(actual, expected)
        ira.level_up(16)
        ira.promote()
        ira.level_up(10)
        self.assertEqual(ira.current_lv, 30)
        with self.assertRaises(LevelUpError):
            ira.level_up(1)

    def test_arden(self):
        """
        """
        arden = Morph4("Arden")
        self.assertEqual(arden.current_lv, 3)
        with self.assertRaises(PromotionError) as exc_ctx:
            arden.promote()
        actual = exc_ctx.exception.reason
        expected = PromotionError.Reason.LEVEL_TOO_LOW
        self.assertEqual(actual, expected)
        arden.level_up(17)
        arden.promote()
        with self.assertRaises(PromotionError) as err_ctx:
            arden.promote()
        expected = err_ctx.exception.reason
        actual = PromotionError.Reason.NO_PROMOTIONS
        self.assertEqual(actual, expected)
        arden.level_up(10)
        with self.assertRaises(LevelUpError):
            arden.level_up(1)

    def test_lakche_with_father_lex(self):
        """
        """
        lakche = Morph4("Lakche", father="Lex")
        self.assertEqual(lakche.current_lv, 1)
        with self.assertRaises(PromotionError) as exc_ctx:
            lakche.promote()
        actual = exc_ctx.exception.reason
        expected = PromotionError.Reason.LEVEL_TOO_LOW
        self.assertEqual(actual, expected)
        lakche.level_up(19)
        lakche.promote()
        lakche.level_up(10)
        with self.assertRaises(LevelUpError):
            lakche.level_up(1)

    def test_lakche_as_bastard(self):
        """
        """
        with self.assertRaises(UnitNotFoundError) as err_ctx:
            Morph4("Lakche", father="")
        # generate father list
        actual = err_ctx.exception.unit_type
        expected = UnitNotFoundError.UnitType.FATHER
        self.assertEqual(actual, expected)
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
        (err_msg,) = err_ctx.exception.args
        self.assertIn("%r" % (tuple(father_list),), err_msg)
        logger.debug("%s", father_list)

    def test_get_promotion_item__promotables(self):
        """
        """
        promotables = self._get_promotables(can_promote=True)
        expected = "*Promote at Base*"
        for name in promotables:
            morph = Morph4(name, father="Lex")
            actual = morph.get_promotion_item()
            self.assertEqual(actual, expected)
            # extra
            morph.level_up(20 - morph.current_lv)
            morph.promote()
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)

    def test_get_promotion_item__nonpromotables(self):
        """
        """
        nonpromotables = self._get_promotables(can_promote=False)
        for name in nonpromotables:
            morph = Morph4(name, father="Lex")
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)

    def test_nonkids_who_can_promote(self):
        """
        """
        promotables = self._get_promotables(can_promote=True)
        kids = self._get_kid_list()
        for name in filter(lambda unit: unit not in kids, promotables):
            logger.debug("Now inspecting: '%s'", name)
            morph = Morph4(name)
            morph.level_up(20 - morph.current_lv)
            morph.promote()
            morph.level_up(10)
            with self.assertRaises(LevelUpError):
                morph.level_up(1)

    def test_nonkids_who_cannot_promote(self):
        """
        """
        promotables = self._get_promotables(can_promote=False)
        kids = self._get_kid_list()
        for name in filter(lambda unit: unit not in kids, promotables):
            logger.debug("Now inspecting: '%s'", name)
            morph = Morph4(name)
            #morph.level_up(20 - morph.current_lv)
            #morph.promote()
            morph.level_up(30 - morph.current_lv)
            with self.assertRaises(LevelUpError):
                morph.level_up(1)

    def test_kids_who_can_promote(self):
        """
        """
        promotables = self._get_promotables(can_promote=True)
        kids = self._get_kid_list()
        fathers = self._get_father_list()
        for name in filter(lambda unit: unit in kids, promotables):
            for father in fathers:
                logger.debug("Now inspecting: '%s' with father as '%s'", name, father)
                morph = Morph4(name, father=father)
                morph.level_up(20 - morph.current_lv)
                morph.promote()
                morph.level_up(10)
                with self.assertRaises(LevelUpError):
                    morph.level_up(1)

    def test_kids_who_cannot_promote(self):
        """
        """
        promotables = self._get_promotables(can_promote=False)
        kids = self._get_kid_list()
        fathers = self._get_father_list()
        for name in filter(lambda unit: unit in kids, promotables):
            for father in fathers:
                logger.debug("Now inspecting: '%s' with father as '%s'", name, father)
                morph = Morph4(name, father=father)
                #morph.level_up(20 - morph.current_lv)
                #morph.promote()
                morph.level_up(30 - morph.current_lv)
                with self.assertRaises(LevelUpError):
                    morph.level_up(1)

    def test_use_stat_booster(self):
        """
        """
        sigurd = Morph4("Sigurd")
        with self.assertRaises(StatBoosterError) as err_ctx:
            sigurd.use_stat_booster(None, None)
        actual = err_ctx.exception.reason
        expected = StatBoosterError.Reason.NO_IMPLEMENTATION
        self.assertEqual(actual, expected)

    def test_inventory_size(self):
        """
        """
        sigurd = Morph4("Sigurd")
        actual = sigurd.inventory_size
        expected = 7
        self.assertEqual(actual, expected)

class Morph5Tests(unittest.TestCase):
    """
    """

    def tearDown(self):
        """
        """
        logger.critical("%s", self.id())

    def setUp(self):
        """
        """
        logger.critical("%s", self.id())
        self.scrolls = (
            "Odo",
            "Baldo",
            "Hezul",
            "Dain",
            "Noba",
            "Neir",
            "Ulir",
            "Tordo",
            "Fala",
            "Sety",
            "Blaggi",
            "Heim",
        )
        self.eda = Morph5("Eda")

    @staticmethod
    def _get_promotables(can_promote):
        """
        """
        # query for list of units who cannot promote
        url_name = "thracia-776"
        return _get_promotables(url_name, can_promote=can_promote)

    def test_get_promotion_item__leif(self):
        """
        """
        name = "Leaf"
        morph = Morph5(name)
        actual = morph.get_promotion_item()
        expected = "*Chapter 18 - End*"
        self.assertEqual(actual, expected)
        morph.promote()
        actual = morph.get_promotion_item()
        self.assertIsNone(actual)

    def test_get_promotion_item__linoan(self):
        """
        """
        name = "Linoan"
        morph = Morph5(name)
        actual = morph.get_promotion_item()
        expected = "*Chapter 21 - Church*"
        self.assertEqual(actual, expected)
        morph.promote()
        actual = morph.get_promotion_item()
        self.assertIsNone(actual)

    def test_get_promotion_item__lara(self):
        """
        """
        name = "Lara"
        morph = Morph5(name)
        morph.promo_cls = "Dancer"
        actual = morph.get_promotion_item()
        expected = "*Chapter 12x - Talk to Perne*"
        self.assertEqual(actual, expected)
        morph.promote() # to: Dancer
        actual = morph.get_promotion_item()
        expected = "Knight Proof"
        self.assertEqual(actual, expected)
        morph.level_up(10 - morph.current_lv)
        morph.promote() # to: Thief Fighter
        actual = morph.get_promotion_item()
        self.assertIsNone(actual)

    def test_get_promotion_item__lara_as_thief_fighter(self):
        """
        """
        name = "Lara"
        morph = Morph5(name)
        morph.level_up(10 - morph.current_lv)
        morph.promo_cls = "Thief Fighter"
        actual = morph.get_promotion_item()
        expected = "Knight Proof"
        self.assertEqual(actual, expected)
        morph.promote() # to Thief Fighter
        actual = morph.get_promotion_item()
        expected = "*Chapter 12x - Talk to Perne*"
        self.assertEqual(actual, expected)
        morph.promote() # to Dancer
        morph.level_up(10 - morph.current_lv)
        actual = morph.get_promotion_item()
        expected = "Knight Proof"
        morph.promote() # to Thief Fighter
        actual = morph.get_promotion_item()
        self.assertIsNone(actual)

    def test_get_promotion_item__promotables(self):
        """
        """
        promotables = self._get_promotables(can_promote=True)
        expected = "Knight Proof"
        exceptions = ("Leaf", "Linoan", "Lara")
        for name in filter(lambda name_: name_ not in exceptions, promotables):
            morph = Morph5(name)
            actual = morph.get_promotion_item()
            self.assertEqual(actual, expected)
            # extra
            morph.level_up(20 - morph.current_lv)
            morph.promote()
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)

    def test_get_promotion_item__nonpromotables(self):
        """
        """
        nonpromotables = self._get_promotables(can_promote=False)
        for name in nonpromotables:
            morph = Morph5(name)
            actual = morph.get_promotion_item()
            logger.debug("Promo-item for '%s' is: '%s'", name, actual)
            self.assertIsNone(actual)


    def test_apply_scroll_bonuses__negatives_are_zeroed_out(self):
        """
        """
        eda = self.eda
        eda.equipped_scrolls[None] = eda.Stats(**eda.Stats.get_stat_dict(-200))
        eda._apply_scroll_bonuses()
        actual = all(eda.growth_rates == eda.Stats(**eda.Stats.get_stat_dict(0)))
        expected = True
        self.assertIs(actual, expected)

    def test_get_promotion_item__has_been_promoted(self):
        """
        """
        morph = Morph5("Leaf")
        morph.promote()
        #with self.assertRaises(ValueError):
        actual = morph.get_promotion_item()
        self.assertIsNone(actual)

    @unittest.skip("Is already covered by another test.")
    def test_get_promotion_item__lara_promotes_to_dancer(self):
        """
        """
        morph = Morph5("Lara")
        morph.promo_cls = "Dancer"
        #morph.promote()
        actual = morph.get_promotion_item()
        self.assertIsNone(actual)

    #@unittest.expectedFailure
    def test_get_promotion_item__promoted(self):
        """
        """
        morph = Morph5("Evayle")
        #with self.assertRaises(ValueError):
        actual = morph.get_promotion_item()
        self.assertIsNone(actual)

    def test_get_promotion_item__lara_is_maxed_out(self):
        """
        """
        morph = Morph5("Lara")
        morph.promo_cls = "Dancer"
        morph.promote()
        morph.level_up(10 - morph.current_lv)
        morph.promote()
        #with self.assertRaises(ValueError):
        actual = morph.get_promotion_item()
        self.assertIsNone(actual)

    def test_get_promotion_item__leif(self):
        """
        """
        morph = Morph5("Leaf")
        actual = morph.get_promotion_item()
        expected = "*Chapter 18 - End*"
        self.assertEqual(actual, expected)

    def test_inventory_size(self):
        """
        """
        morph = Morph5("Leaf")
        actual = morph.inventory_size
        self.assertIsInstance(actual, int)
        self.assertGreater(actual, 0)

    def test_linoan__promotion(self):
        """
        """
        name = "Linoan"
        morph = Morph5(name)
        self.assertLess(morph.current_lv, 10)
        #self.assertEqual(morph.current_lv, 1)
        morph.promote()
        self.assertEqual(morph.current_clstype, "classes__promotion_gains")
        with self.assertRaises(PromotionError):
            morph.promote()

    def test_leif__promotion(self):
        """
        """
        name = "Leaf"
        morph = Morph5(name)
        self.assertLess(morph.current_lv, 10)
        #self.assertEqual(morph.current_lv, 1)
        morph.promote()
        self.assertEqual(morph.current_clstype, "classes__promotion_gains")
        with self.assertRaises(PromotionError):
            morph.promote()

    def test_promotables(self):
        """
        """
        promotables = self._get_promotables(can_promote=True)
        logger.debug("%s", promotables)
        for name in filter(lambda name: name != "Lara", promotables):
            morph = Morph5(name)
            morph.level_up(20 - morph.current_lv)
            morph.promote()
            morph.level_up(19)
            with self.assertRaises(LevelUpError):
                morph.level_up(1)

    def test_nonpromotables(self):
        """
        """
        nonpromotables = self._get_promotables(can_promote=False)
        logger.debug("%s", nonpromotables)
        for name in nonpromotables:
            morph = Morph5(name)
            morph.level_up(20 - morph.current_lv)
            with self.assertRaises(LevelUpError):
                morph.level_up(1)

    def test_lara__long_path(self):
        """
        """
        # Thief -> Thief Fighter -> Dancer -> Thief Fighter
        lara = Morph5("Lara")
        lara.level_up(10 - lara.current_lv)
        with self.assertRaises(PromotionError) as err_ctx:
            lara.promote()
        (err_msg,) = err_ctx.exception.args
        valid_promotions = ('Thief Fighter', 'Dancer')
        self.assertIn(str(valid_promotions), err_msg)
        lara.promo_cls = "Thief Fighter"
        lara.promote()
        #lara.promo_cls = "Dancer"
        #lara.current_lv = 10
        #with self.assertRaises(KeyError) as err_ctx:
        lara.promote()
        lara.current_lv = 10
        lara.promote()
        logger.debug("class: '%s', level: %d", lara.current_cls, lara.current_lv)
        with self.assertRaises(PromotionError) as err_ctx:
            lara.promote()
        expected = err_ctx.exception.reason
        actual = PromotionError.Reason.NO_PROMOTIONS
        self.assertEqual(actual, expected)
        #logger.debug("%s", err_ctx.exception.args)

    def test_lara__short_path(self):
        """
        """
        # Thief -> Dancer -> Thief Fighter
        lara = Morph5("Lara")
        lara.promo_cls ="Dancer"
        lara.promote()
        with self.assertRaises(PromotionError) as exc_ctx:
            lara.promote()
        actual = exc_ctx.exception.reason
        expected = PromotionError.Reason.LEVEL_TOO_LOW
        self.assertEqual(actual, expected)
        lara.level_up(9)
        lara.promote()
        with self.assertRaises(PromotionError) as err_ctx:
            lara.promote()
        expected = err_ctx.exception.reason
        actual = PromotionError.Reason.NO_PROMOTIONS
        self.assertEqual(actual, expected)

    def test_scroll_level_up(self):
        """
        """
        eda = Morph5("Eda")
        eda.equip_scroll("Blaggi")
        eda.equip_scroll("Heim")
        eda.equip_scroll("Fala")
        eda.unequip_scroll("Fala")
        with self.assertRaises(ScrollError) as err_ctx:
            eda.unequip_scroll("")
        actual = err_ctx.exception.reason
        expected = ScrollError.Reason.NOT_EQUIPPED
        self.assertEqual(actual, expected)
        with self.assertRaises(ScrollError) as err_ctx:
            eda.equip_scroll("Heim")
        actual = err_ctx.exception.reason
        expected = ScrollError.Reason.ALREADY_EQUIPPED
        self.assertEqual(actual, expected)
        with self.assertRaises(ScrollError) as err_ctx:
            eda.equip_scroll("")
        actual = err_ctx.exception.reason
        expected = ScrollError.Reason.NOT_FOUND
        self.assertEqual(actual, expected)
        eda.level_up(10)
        eda2 = Morph5("Eda")
        eda2.level_up(10)
        self.assertEqual(eda.current_stats.Str - eda2.current_stats.Str, -1)
        self.assertEqual(eda.current_stats.Mag - eda2.current_stats.Mag, 4)
        self.assertEqual(eda.current_stats.Lck - eda2.current_stats.Lck, 4)
        self.assertEqual(eda.current_stats.Def - eda2.current_stats.Def, -1)

    def test_equip_scroll(self):
        """
        """
        scroll_name = self.scrolls[0]
        og_growths = self.eda.growth_rates.copy()
        self.eda.equip_scroll(scroll_name)
        self.assertIn(scroll_name, self.eda.equipped_scrolls)
        self.assertEqual(len(self.eda.equipped_scrolls), 1)
        new_growths = self.eda.growth_rates
        actual = all(og_growths == new_growths)
        expected = False
        self.assertIs(actual, expected)
        with self.assertRaises(ScrollError) as err_ctx:
            self.eda.equip_scroll(scroll_name)
        actual = err_ctx.exception.reason
        expected = ScrollError.Reason.ALREADY_EQUIPPED
        self.assertEqual(actual, expected)

    def test_equip_scroll__exceed_inventory_space(self):
        """
        """
        # equip scrolls
        eda = self.eda
        for i in range(7):
            scroll_name = self.scrolls[i]
            eda.equip_scroll(scroll_name)
        # affirm size of equipped scrolls
        self.assertGreater(len(self.scrolls), len(eda.equipped_scrolls))
        # try to equip another scroll
        scroll_name = self.scrolls[-1]
        with self.assertRaises(ScrollError) as err_ctx:
            eda.equip_scroll(scroll_name)
        actual = err_ctx.exception.reason
        expected = ScrollError.Reason.NO_INVENTORY_SPACE
        self.assertEqual(actual, expected)

    def test_equip_scroll__scroll_dne(self):
        """
        """
        scroll_name = ""
        og_growths = self.eda.growth_rates.copy()
        with self.assertRaises(ScrollError) as err_ctx:
            self.eda.equip_scroll(scroll_name)
        # check error
        actual = err_ctx.exception.reason
        expected = ScrollError.Reason.NOT_FOUND
        self.assertEqual(actual, expected)
        # check state
        self.assertNotIn(scroll_name, self.eda.equipped_scrolls)
        self.assertEqual(len(self.eda.equipped_scrolls), 0)
        new_growths = self.eda.growth_rates
        actual = all(og_growths == new_growths)
        expected = True
        self.assertIs(actual, expected)

    def test_use_stat_booster__maxed_stat(self):
        """
        """
        leaf = Morph5("Leaf")
        leaf.current_stats.Spd = 20
        with self.assertRaises(StatBoosterError) as exception_ctx:
            leaf.use_stat_booster("Speed Ring")
        exception = exception_ctx.exception
        actual = exception.reason
        expected = StatBoosterError.Reason.STAT_IS_MAXED
        self.assertEqual(actual, expected)

    def test_inventory_size(self):
        """
        """
        leaf = Morph5("Leaf")
        actual = leaf.inventory_size
        expected = 7
        self.assertEqual(actual, expected)

class Morph6Tests(unittest.TestCase):
    """
    """

    def tearDown(self):
        """
        """
        logger.critical("%s", self.id())

    def setUp(self):
        """
        """
        logger.critical("%s", self.id())

    @staticmethod
    def _get_promotables(can_promote):
        """
        """
        url_name = "binding-blade"
        return _get_promotables(url_name, can_promote)

    def test_get_promotion_item__promotables(self):
        """
        """
        promotables = self._get_promotables(can_promote=True)
        promoitem_dict = {
            'Roy': "*Chapter 22 - Start*",
            #'Marcus':
            'Allen': "Knight Crest",
            'Lance': "Knight Crest",
            'Wolt': "Orion's Bolt",
            'Bors': "Knight Crest",
            #'Merlinus':
            'Ellen': "Guiding Ring",
            'Dieck': "Hero Crest",
            'Wade': "Hero Crest",
            'Lott': "Hero Crest",
            'Thany': "Elysian Whip",
            #'Chad':
            'Lugh': "Guiding Ring",
            'Clarine': "Guiding Ring",
            'Rutger': "Hero Crest",
            #'Rutger (HM)':
            'Saul': "Guiding Ring",
            'Dorothy': "Orion's Bolt",
            'Sue': "Orion's Bolt",
            #'Zealot':
            'Treck': "Knight Crest",
            'Noah': "Knight Crest",
            #'Astohl':
            'Lilina': "Guiding Ring",
            'Wendy': "Knight Crest",
            'Barth': "Knight Crest",
            'Oujay': "Hero Crest",
            'Fir': "Hero Crest",
            #'Fir (HM)':
            'Shin': "Orion's Bolt",
            #'Shin (HM)':
            'Gonzales': "Hero Crest",
            #'Gonzales (HM)':
            'Geese': "Hero Crest",
            #'Klein':
            #'Klein (HM)':
            'Tate': "Elysian Whip",
            #'Tate (HM)':
            #'Lalum':
            #'Echidna':
            #'Elphin':
            #'Bartre':
            'Ray': "Guiding Ring",
            #'Cath':
            #'Cath (HM)':
            'Miredy': "Elysian Whip",
            #'Miredy (HM)':
            #'Percival':
            #'Percival (HM)':
            #'Cecilia':
            'Sofiya': "Guiding Ring",
            #'Igrene':
            #'Garret':
            #'Garret (HM)':
            #'Fa':
            'Hugh': "Guiding Ring",
            'Zeis': "Elysian Whip",
            #'Zeis (HM)':
            #'Douglas':
            #'Niime':
            #'Dayan':
            #'Juno':
            #'Yodel':
            #'Karel':
            #'Narshen':
            #'Gale':
            #'Hector':
            #'Brunya':
            #'Eliwood':
            #'Murdoch':
            #'Zephiel':
            #'Guinevere':
        }
        for name in filter(lambda name_: " (HM)" not in name_, promotables):
            try:
                morph = Morph6(name)
            except InitError:
                morph = Morph6(name, hard_mode=True)
            actual = morph.get_promotion_item()
            expected = promoitem_dict.pop(name)
            self.assertEqual(actual, expected)
            # extra
            morph.level_up(20 - morph.current_lv)
            morph.promote()
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)

    def test_get_promotion_item__nonpromotables(self):
        """
        """
        nonpromotables = self._get_promotables(can_promote=False)
        #expected = None
        for name in filter(lambda name_: " (HM)" not in name_, nonpromotables):
            try:
                morph = Morph6(name)
            except InitError:
                morph = Morph6(name, hard_mode=True)
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)

    def test_as_string(self):
        """
        """
        morph = Morph6("Hugh")
        actual = morph.as_string()
        self.assertIsInstance(actual, str)
        logger.debug("as_string -> %s", actual)

    def test_inventory_size(self):
        """
        """
        morph = Morph6("Roy")
        actual = morph.inventory_size
        self.assertIsInstance(actual, int)
        self.assertGreater(actual, 0)

    def test_get_true_character_list6(self):
        """
        """
        expected = (
            'Roy',
            'Marcus',
            'Allen',
            'Lance',
            'Wolt',
            'Bors',
            'Merlinus',
            'Ellen',
            'Dieck',
            'Wade',
            'Lott',
            'Thany',
            'Chad',
            'Lugh',
            'Clarine',
            'Rutger',
            'Saul',
            'Dorothy',
            'Sue',
            'Zealot',
            'Treck',
            'Noah',
            'Astohl',
            'Lilina',
            'Wendy',
            'Barth',
            'Oujay',
            'Fir',
            'Shin',
            'Gonzales',
            'Geese',
            'Klein',
            'Tate',
            'Lalum',
            'Echidna',
            'Elphin',
            'Bartre',
            'Ray',
            'Cath',
            'Miredy',
            'Percival',
            'Cecilia',
            'Sofiya',
            'Igrene',
            'Garret',
            'Fa',
            'Hugh',
            'Zeis',
            'Douglas',
            'Niime',
            'Dayan',
            'Juno',
            'Yodel',
            'Karel',
            'Narshen',
            'Gale',
            'Hector',
            'Brunya',
            'Eliwood',
            'Murdoch',
            'Zephiel',
            'Guinevere',
        )
        actual = tuple(Morph6.get_true_character_list())
        self.assertTupleEqual(actual, expected)

    def test_roy__early_promotion(self):
        """
        """
        name = "Roy"
        morph = Morph6(name)
        self.assertEqual(morph.current_lv, 1)
        morph.promote()
        self.assertEqual(morph.current_clstype, "classes__promotion_gains")

    def test_not_gonzales_in_elffin_route(self):
        """
        """
        cath = Morph6("Cath", hard_mode=True)
        with self.assertRaises(ValueError):
            cath.set_elffin_route_for_gonzales()

    def test_gonzales_in_elffin_route__already_levelled_up(self):
        """
        """
        gonzales = Morph6("Gonzales", hard_mode=True)
        gonzales.level_up(1)
        with self.assertRaises(InitError):
            gonzales.set_elffin_route_for_gonzales()

    def test_gonzales_in_elffin_route__already_promoted(self):
        """
        """
        gonzales = Morph6("Gonzales", hard_mode=False)
        gonzales.level_up(5)
        gonzales.promote()
        with self.assertRaises(InitError):
            gonzales.set_elffin_route_for_gonzales()

    def test_gonzales_in_elffin_route(self):
        """
        """
        gonzales = Morph6("Gonzales", hard_mode=True)
        gonzales.set_elffin_route_for_gonzales()
        actual = gonzales.current_lv
        expected = 11
        self.assertEqual(actual, expected)

    def test_hugh__already_levelled_up(self):
        """
        """
        hugh = Morph6("Hugh")
        hugh.level_up(1)
        with self.assertRaises(InitError):
            hugh.decline_hugh()

    def test_hugh__already_been_promoted(self):
        """
        """
        hugh = Morph6("Hugh")
        hugh.promote()
        with self.assertRaises(InitError):
            hugh.decline_hugh()

    def test_hugh(self):
        """
        """
        hugh = Morph6("Hugh")
        hugh.decline_hugh()
        hugh.decline_hugh()
        hugh.decline_hugh()
        with self.assertRaises(OverflowError):
            hugh.decline_hugh()
        hugh2 = Morph6("Hugh")
        diff = (hugh.current_stats - hugh2.current_stats).as_dict()
        self.assertSetEqual(set(diff.values()), {-3, None})
        self.assertEqual(hugh._meta["Number of Declines"], 3)
        self.assertEqual(hugh2._meta["Number of Declines"], 0)

    def test_not_hugh(self):
        """
        """
        marcus = Morph6("Marcus")
        with self.assertRaises(ValueError):
            marcus.decline_hugh()
        self.assertIsNone(marcus._meta["Number of Declines"])

    def test_rutger_no_hardmode_specified(self):
        """
        """
        with self.assertRaises(InitError) as exc_ctx:
            rutger = Morph6("Rutger")
        exception = exc_ctx.exception
        actual = exception.missing_value
        expected = InitError.MissingValue.HARD_MODE
        self.assertEqual(actual, expected)

    def test_no_hardmode_version(self):
        """
        """
        with self.assertLogs(logger, logging.WARNING):
            wolt = Morph6("Wolt", hard_mode=True)
        self.assertIsNone(wolt._meta["Hard Mode"])

    def test_hardmode_version_exists(self):
        """
        """
        hard_mode = False
        rutger = Morph6("Rutger", hard_mode=hard_mode)
        self.assertIs(rutger._meta["Hard Mode"], hard_mode)
        hard_mode = True
        rutger2 = Morph6("Rutger", hard_mode=hard_mode)
        self.assertIs(rutger2._meta["Hard Mode"], hard_mode)
        self.assertEqual(rutger2.name, "Rutger")

    def test_hardmode_diff(self):
        """
        """
        rutger = Morph6("Rutger", hard_mode=False)
        rutger_hm = Morph6("Rutger", hard_mode=True)
        diff = (rutger.current_stats - rutger_hm.current_stats).as_dict()
        for stat, val in diff.items():
            if stat in ("Mov", "Con"):
                logger.debug("%s is None.", stat)
                self.assertIsNone(val)
            else:
                logger.debug("Difference in %s: %.2f", stat, val)
                self.assertLess(val, 0)

    def test_roy_promo_level(self):
        """
        """
        morph = Morph6("Roy")
        #self.assertEqual(roy.current_lv, 1)
        self.assertLess(morph.current_lv, 10)
        morph.promote()
        self.assertEqual(morph.current_cls, "Master Lord")
        with self.assertRaises(PromotionError):
            morph.promote()

    def test_promotables(self):
        """
        """
        promotables = self._get_promotables(True)
        for name in promotables:
            hard_mode = " (HM)" in name
            name = name.replace(" (HM)", "")
            logger.debug("Morph6(%r, hard_mode=%r)", name, hard_mode)
            morph = Morph6(name, hard_mode=hard_mode)
            morph.level_up(20 - morph.current_lv)
            morph.promote()
            morph.level_up(19)
            with self.assertRaises(LevelUpError):
                morph.level_up(1)
            with self.assertRaises(PromotionError) as err_ctx:
                morph.promote()
            expected = err_ctx.exception.reason
            actual = PromotionError.Reason.NO_PROMOTIONS
            self.assertEqual(actual, expected)

    def test_nonpromotables(self):
        """
        """
        nonpromotables = self._get_promotables(False)
        for name in nonpromotables:
            hard_mode = " (HM)" in name
            name = name.replace(" (HM)", "")
            logger.debug("Morph6(%r, hard_mode=%r)", name, hard_mode)
            morph = Morph6(name, hard_mode=hard_mode)
            with self.assertRaises(PromotionError) as exc_ctx:
                morph.promote()
            actual = exc_ctx.exception.reason
            expected = PromotionError.Reason.NO_PROMOTIONS
            self.assertEqual(actual, expected)
            morph.level_up(20 - morph.current_lv)
            #morph.promote()
            #morph.level_up(19)
            with self.assertRaises(LevelUpError):
                morph.level_up(1)

    def test_stat_boosters(self):
        """
        """
        item_bonus_dict = {
            "Angelic Robe": ("HP", 7),
            "Energy Ring": ("Pow", 2),
            "Secret Book": ("Skl", 2),
            "Speedwings": ("Spd", 2),
            "Goddess Icon": ("Lck", 2),
            "Dragonshield": ("Def", 2),
            "Talisman": ("Res", 2),
            "Boots": ("Mov", 2),
            "Body Ring": ("Con", 3),
        }
        morph = Morph6("Roy")
        for item, statbonus in item_bonus_dict.items():
            original_stats = morph.current_stats.copy()
            morph.use_stat_booster(item)
            stat, bonus = statbonus
            expected = getattr(original_stats, stat) + bonus
            actual = getattr(morph.current_stats, stat)
            self.assertEqual(actual, expected)

    def test_inventory_size(self):
        """
        """
        lord = Morph6("Roy")
        actual = lord.inventory_size
        expected = 5
        self.assertEqual(actual, expected)

class Morph7Tests(unittest.TestCase):
    """
    """

    def tearDown(self):
        """
        """
        logger.critical("%s", self.id())

    def setUp(self):
        """
        """
        logger.critical("%s", self.id())
        self.lyndis_league = (
            "Lyn",
            "Sain",
            "Kent",
            "Florina",
            "Wil",
            "Dorcas",
            "Serra",
            "Erk",
            "Rath",
            "Matthew",
            "Nils",
            "Lucius",
            "Wallace",
        )

    def test_ninian__lyn_mode(self):
        """
        """
        with self.assertRaises(UnitNotFoundError):
            Morph7("Ninian", lyn_mode=True)

    def test_get_promotion_item__promotables(self):
        """
        """
        promotables = self._get_promotables(can_promote=True)
        promoitem_dict = {
            'Lyn': "Heaven Seal",
            'Sain': "Knight Crest",
            'Kent': "Knight Crest",
            'Florina': "Elysian Whip",
            'Wil': "Orion's Bolt",
            'Dorcas': "Hero Crest",
            'Serra': "Guiding Ring",
            'Erk': "Guiding Ring",
            'Rath': "Orion's Bolt",
            'Matthew': "Fell Contract",
            #'Nils':
            'Lucius': "Guiding Ring",
            'Wallace': "Knight Crest",
            'Eliwood': "Heaven Seal",
            'Lowen': "Knight Crest",
            #'Marcus':
            'Rebecca': "Orion's Bolt",
            'Bartre': "Hero Crest",
            'Hector': "Heaven Seal",
            'Oswin': "Knight Crest",
            'Guy': "Hero Crest",
            #'Guy (HM)':
            #'Merlinus':
            'Priscilla': "Guiding Ring",
            'Raven': "Hero Crest",
            #'Raven (HM)':
            'Canas': "Guiding Ring",
            'Dart': "Ocean Seal",
            'Fiora': "Elysian Whip",
            'Legault': "Fell Contract",
            #'Legault (HM)':
            #'Ninian':
            #'Isadora':
            'Heath': "Elysian Whip",
            #'Hawkeye':
            #'Geitz':
            #'Geitz (HM)':
            'Farina': "Elysian Whip",
            #'Pent':
            #'Louise':
            #'Karel':
            #'Harken':
            #'Harken (HM)':
            'Nino': "Guiding Ring",
            #'Jaffar':
            #'Vaida':
            #'Vaida (HM)':
            #'Karla':
            #'Renault':
            #'Athos':
        }
        for name in filter(lambda name_: " (HM)" not in name_, promotables):
            if name in self.lyndis_league:
                morph = Morph7(name, lyn_mode=True)
            else:
                try:
                    morph = Morph7(name)
                except InitError:
                    morph = Morph7(name, hard_mode=True)
            actual = morph.get_promotion_item()
            expected = promoitem_dict.pop(name)
            self.assertEqual(actual, expected)
            # extra
            morph.level_up(20 - morph.current_lv)
            morph.promote()
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)

    def test_get_promotion_item__nonpromotables(self):
        """
        """
        nonpromotables = self._get_promotables(can_promote=False)
        #expected = None
        for name in nonpromotables:
            if name in self.lyndis_league:
                morph = Morph7(name, lyn_mode=False)
            else:
                try:
                    morph = Morph7(name)
                except InitError:
                    morph = Morph7(name, hard_mode=True)
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)

    def test_inventory_size(self):
        """
        """
        morph = Morph7("Hector")
        actual = morph.inventory_size
        self.assertIsInstance(actual, int)
        self.assertGreater(actual, 0)

    def test_hector__early_promotion(self):
        """
        """
        name = "Hector"
        morph = Morph7(name)
        self.assertLess(morph.current_lv, 10)
        #self.assertEqual(morph.current_lv, 1)
        morph.promote()
        self.assertEqual(morph.current_clstype, "classes__promotion_gains")
        with self.assertRaises(PromotionError):
            morph.promote()

    def test_eliwood__early_promotion(self):
        """
        """
        name = "Eliwood"
        morph = Morph7(name)
        self.assertLess(morph.current_lv, 10)
        #self.assertEqual(morph.current_lv, 1)
        morph.promote()
        self.assertEqual(morph.current_clstype, "classes__promotion_gains")
        with self.assertRaises(PromotionError):
            morph.promote()

    @staticmethod
    def _get_promotables(can_promote):
        """
        """
        # query for list of units who cannot promote
        url_name = "blazing-sword"
        return _get_promotables(url_name, can_promote=can_promote)

    def test_get_true_character_list7(self):
        """
        """
        expected = (
            'Lyn',
            'Sain',
            'Kent',
            'Florina',
            'Wil',
            'Dorcas',
            'Serra',
            'Erk',
            'Rath',
            'Matthew',
            'Nils',
            'Lucius',
            'Wallace',
            'Eliwood',
            'Lowen',
            'Marcus',
            'Rebecca',
            'Bartre',
            'Hector',
            'Oswin',
            'Guy',
            'Merlinus',
            'Priscilla',
            'Raven',
            'Canas',
            'Dart',
            'Fiora',
            'Legault',
            'Ninian',
            'Isadora',
            'Heath',
            'Hawkeye',
            'Geitz',
            'Farina',
            'Pent',
            'Louise',
            'Karel',
            'Harken',
            'Nino',
            'Jaffar',
            'Vaida',
            'Karla',
            'Renault',
            'Athos',
        )
        actual = tuple(Morph7.get_true_character_list())
        self.assertTupleEqual(actual, expected)

    def test_raven_no_hardmode_specified(self):
        """
        """
        with self.assertRaises(InitError) as exc_ctx:
            raven = Morph7("Raven")
        exception = exc_ctx.exception
        actual = exception.missing_value
        expected = InitError.MissingValue.HARD_MODE
        self.assertEqual(actual, expected)

    def test_lyn_no_lynmode_specified(self):
        """
        """
        with self.assertRaises(InitError) as exc_ctx:
            raven = Morph7("Lyn")
        exception = exc_ctx.exception
        actual = exception.missing_value
        expected = InitError.MissingValue.LYN_MODE
        self.assertEqual(actual, expected)

    def test_copy(self):
        """
        """
        raven = Morph7("Raven", hard_mode=True)
        raven_clone = raven.copy()
        raven.level_up(15)
        raven.promote()
        base_raven = Morph7("Raven", hard_mode=True)
        actual = raven_clone.current_lv
        expected = base_raven.current_lv
        self.assertEqual(actual, expected)
        actual = raven_clone.current_cls
        expected = base_raven.current_cls
        self.assertEqual(actual, expected)
        actual = raven_clone.current_stats
        expected = base_raven.current_stats
        self.assertEqual(actual, expected)
        actual = raven_clone._meta
        expected = raven._meta
        self.assertIsNot(actual, expected)
        for stat in raven.Stats.STAT_LIST():
            actual = getattr(raven.current_stats, stat)
            expected = getattr(raven_clone.current_stats, stat)
            self.assertGreater(actual, expected)

    def test_afas_drops(self):
        """
        """
        nino = Morph7("Nino")
        nino.use_afas_drops()
        nino2 = Morph7("Nino")
        diff = (nino.growth_rates - nino2.growth_rates).as_dict()
        self.assertSetEqual(set(diff.values()), {5, None})
        with self.assertRaises(GrowthsItemError) as err_ctx:
            nino.use_afas_drops()
        actual = err_ctx.exception.reason
        expected = GrowthsItemError.Reason.ALREADY_CONSUMED
        self.assertEqual(actual, expected)

    def test_no_hardmode_version(self):
        """
        """
        with self.assertLogs(logger, logging.WARNING):
            matthew = Morph7("Matthew", hard_mode=True, lyn_mode=True)
        self.assertIsNone(matthew._meta["Hard Mode"])

    def test_hardmode_version_exists(self):
        """
        """
        hard_mode = False
        guy = Morph7("Guy", hard_mode=hard_mode)
        self.assertIs(guy._meta["Hard Mode"], hard_mode)
        hard_mode = True
        guy2 = Morph7("Guy", hard_mode=hard_mode)
        self.assertIs(guy2._meta["Hard Mode"], hard_mode)
        self.assertEqual(guy2.name, "Guy")

    def test_hardmode_diff(self):
        """
        """
        guy = Morph7("Guy", hard_mode=False)
        guy_hm = Morph7("Guy", hard_mode=True)
        diff = (guy.current_stats - guy_hm.current_stats).as_dict()
        for stat, val in diff.items():
            if stat == "Lck":
                logger.debug("Stat is 'Lck'. Expecting zero-diff.")
                self.assertEqual(val, 0)
                continue
            if stat in ("Mov", "Con"):
                logger.debug("Stat is %s. Expecting None.", stat)
                self.assertIsNone(val)
                continue
            logger.debug("Difference in %s: %.2f", stat, val)
            self.assertLess(val, 0)

    def test_not_in_lyndis_league(self):
        """
        """
        with self.assertLogs(logger, logging.WARNING):
            athos = Morph7("Athos", lyn_mode=True)
        self.assertIsNone(athos._meta["Lyn Mode"])

    def test_lyn(self):
        """
        """
        lyn = Morph7("Lyn", lyn_mode=True)
        self.assertIs(lyn._meta["Lyn Mode"], True)
        lyn2 = Morph7("Lyn", lyn_mode=False)
        self.assertIs(lyn2._meta["Lyn Mode"], False)
        diff = (lyn.current_stats - lyn2.current_stats).as_dict()
        self.assertNotEqual(set(diff.values()), {0})

    def test_wallace__unpromoted(self):
        """
        """
        wallace = Morph7("Wallace", lyn_mode=True)
        wallace.level_up(20 - wallace.current_lv)
        wallace.promote()
        wallace.level_up(19)

    def test_wallace__promoted(self):
        """
        """
        wallace = Morph7("Wallace", lyn_mode=False)
        wallace.level_up(20 - wallace.current_lv)
        with self.assertRaises(PromotionError) as err_ctx:
            wallace.promote()
        expected = err_ctx.exception.reason
        actual = PromotionError.Reason.NO_PROMOTIONS
        self.assertEqual(actual, expected)
        #wallace.level_up(19)

    def test_hardmode_override(self):
        """
        """
        # documents what happens when you try to manually query HM version of character
        raven = Morph7("Raven (HM)", hard_mode=False)
        self.assertIsNone(raven._meta["Hard Mode"])
        raven2 = Morph7("Raven", hard_mode=True)
        self.assertIs(raven2._meta["Hard Mode"], True)
        diff = (raven.current_stats - raven2.current_stats).as_dict()
        self.assertSetEqual(set(diff.values()), {0, None})

    def test_lyndis_league(self):
        """
        """
        lyndis_league = self.lyndis_league
        for name in filter(lambda name: name != "Wallace", lyndis_league):
            logger.debug("name: '%s'", name)
            morph = Morph7(name, lyn_mode=True)
            self.assertIs(morph._meta["Lyn Mode"], True)
            morph2 = Morph7(name, lyn_mode=False)
            self.assertIs(morph2._meta["Lyn Mode"], False)
            diff = (morph.current_stats - morph2.current_stats).as_dict()
            if name in ("Dorcas", "Serra", "Erk", "Matthew", "Nils", "Lucius"):
                logger.debug("'%s' does not differ stat-wise between tutorial and main campaign.", name)
                continue
            self.assertNotEqual(set(diff.values()), {0})

    def test_promotables(self):
        """
        """
        promotables = self._get_promotables(True)
        for name in filter(lambda name: name not in self.lyndis_league, promotables):
            hard_mode = " (HM)" in name
            name = name.replace(" (HM)", "")
            logger.debug("Morph7(%r, hard_mode=%r)", name, hard_mode)
            morph = Morph7(name, hard_mode=hard_mode)
            morph.level_up(20 - morph.current_lv)
            morph.promote()
            morph.level_up(19)
            with self.assertRaises(LevelUpError):
                morph.level_up(1)
            with self.assertRaises(PromotionError) as err_ctx:
                morph.promote()
            expected = err_ctx.exception.reason
            actual = PromotionError.Reason.NO_PROMOTIONS
            self.assertEqual(actual, expected)

    def test_nonpromotables(self):
        """
        """
        nonpromotables = self._get_promotables(False)
        for name in filter(lambda name: name not in self.lyndis_league, nonpromotables):
            hard_mode = " (HM)" in name
            name = name.replace(" (HM)", "")
            logger.debug("Morph7(%r, hard_mode=%r)", name, hard_mode)
            morph = Morph7(name, hard_mode=hard_mode)
            with self.assertRaises(PromotionError) as exc_ctx:
                morph.promote()
            actual = exc_ctx.exception.reason
            expected = PromotionError.Reason.NO_PROMOTIONS
            self.assertEqual(actual, expected)
            morph.level_up(20 - morph.current_lv)
            with self.assertRaises(LevelUpError):
                morph.level_up(1)
            with self.assertRaises(PromotionError) as err_ctx:
                morph.promote()
            expected = err_ctx.exception.reason
            actual = PromotionError.Reason.NO_PROMOTIONS
            self.assertEqual(actual, expected)

    def test_stat_boosters(self):
        """
        """
        item_bonus_dict = {
            "Angelic Robe": ("HP", 7),
            "Energy Ring": ("Pow", 2),
            "Secret Book": ("Skl", 2),
            "Speedwings": ("Spd", 2),
            "Goddess Icon": ("Lck", 2),
            "Dragonshield": ("Def", 2),
            "Talisman": ("Res", 2),
            "Boots": ("Mov", 2),
            "Body Ring": ("Con", 3),
        }
        morph = Morph7("Eliwood")
        for item, statbonus in item_bonus_dict.items():
            original_stats = morph.current_stats.copy()
            morph.use_stat_booster(item)
            stat, bonus = statbonus
            expected = getattr(original_stats, stat) + bonus
            actual = getattr(morph.current_stats, stat)
            self.assertEqual(actual, expected)

    def test_inventory_size(self):
        """
        """
        lord = Morph7("Eliwood")
        actual = lord.inventory_size
        expected = 5
        self.assertEqual(actual, expected)

class Morph8Tests(unittest.TestCase):
    """
    """

    def tearDown(self):
        """
        """
        logger.critical("%s", self.id())

    def setUp(self):
        """
        """
        logger.critical("%s", self.id())
        self.trainees = ("Ross", "Amelia", "Ewan")

    @staticmethod
    def _get_promotables(can_promote):
        """
        """
        # query for list of units who cannot promote
        url_name = "the-sacred-stones"
        return _get_promotables(url_name, can_promote=can_promote)

    def test_get_promotion_item__amelia(self):
        """
        """
        name = "Amelia"
        promotion_item = "Knight Crest"
        self._test_get_promotion_item__trainee(name, promotion_item)

    def test_get_promotion_item__ewan(self):
        """
        """
        name = "Ewan"
        promotion_item = "Guiding Ring"
        self._test_get_promotion_item__trainee(name, promotion_item)

    def test_get_promotion_item__ross(self):
        """
        """
        name = "Ross"
        _morph = Morph8(name)
        _morph.current_lv = 10
        try:
            _morph.promote()
        except PromotionError as error:
            actual = error.reason
            expected = PromotionError.Reason.INVALID_PROMOTION
            self.assertEqual(actual, expected)
        promo_dict = {}
        # compile list of promotions
        for promo_cls in _morph.possible_promotions:
            morph = Morph8(name)
            morph.current_lv = 10
            morph.promo_cls = promo_cls
            morph.promote()
            morph.current_lv = 10
            try:
                morph.promote()
            except PromotionError as error:
                actual = error.reason
                expected = PromotionError.Reason.INVALID_PROMOTION
                self.assertEqual(actual, expected)
            promo_dict[promo_cls] = morph.possible_promotions
        expected1 = "*Reach Level 10*"
        for promo_cls, promoclasses2 in promo_dict.items():
            if promo_cls == "Pirate":
                promotion_item = "Ocean Seal"
            else:
                promotion_item = "Hero Crest"
            for promo_cls2 in promoclasses2:
                morph = Morph8(name)
                # try to promote at base level; this fails
                with self.assertRaises(PromotionError) as exc_ctx:
                    morph.promote()
                actual = exc_ctx.exception.reason
                expected = PromotionError.Reason.LEVEL_TOO_LOW
                self.assertEqual(actual, expected)
                # level up to promotion level
                morph.level_up(10 - morph.current_lv)
                with self.assertRaises(LevelUpError):
                    # level up past promotion level; this fails
                    morph.level_up(1)
                morph.promo_cls = promo_cls
                actual1 = morph.get_promotion_item()
                self.assertEqual(actual1, expected1)
                # promote
                morph.promote()
                # level is reset to 1
                self.assertEqual(morph.current_lv, 1)
                actual2 = morph.get_promotion_item()
                expected2 = promotion_item
                self.assertEqual(actual2, expected2)
                # level up to 20
                morph.level_up(19)
                with self.assertRaises(LevelUpError):
                    # level up past 20; this fails
                    morph.level_up(1)
                morph.promo_cls = promo_cls2
                actual3 = morph.get_promotion_item()
                expected3 = promotion_item
                self.assertEqual(actual3, expected3)
                # final promotion
                morph.promote()
                # level to 20
                morph.level_up(19)
                actual4 = morph.get_promotion_item()
                self.assertIsNone(actual4)
                with self.assertRaises(LevelUpError):
                    # level up past 20; this fails
                    morph.level_up(1)
                with self.assertRaises(PromotionError) as err_ctx:
                    morph.promote()
                (err_msg,) = err_ctx.exception.args
                self.assertIn("no available promotions", err_msg)

    def _test_get_promotion_item__trainee(self, name, promotion_item):
        """
        """
        _morph = Morph8(name)
        _morph.current_lv = 10
        try:
            _morph.promote()
        except PromotionError as error:
            actual = error.reason
            expected = PromotionError.Reason.INVALID_PROMOTION
            self.assertEqual(actual, expected)
        promo_dict = {}
        # compile list of promotions
        for promo_cls in _morph.possible_promotions:
            morph = Morph8(name)
            morph.current_lv = 10
            morph.promo_cls = promo_cls
            morph.promote()
            morph.current_lv = 10
            try:
                morph.promote()
            except PromotionError as error:
                actual = error.reason
                expected = PromotionError.Reason.INVALID_PROMOTION
                self.assertEqual(actual, expected)
            promo_dict[promo_cls] = morph.possible_promotions
        expected1 = "*Reach Level 10*"
        for promo_cls, promoclasses2 in promo_dict.items():
            for promo_cls2 in promoclasses2:
                morph = Morph8(name)
                # try to promote at base level; this fails
                with self.assertRaises(PromotionError) as exc_ctx:
                    morph.promote()
                actual = exc_ctx.exception.reason
                expected = PromotionError.Reason.LEVEL_TOO_LOW
                self.assertEqual(actual, expected)
                # level up to promotion level
                morph.level_up(10 - morph.current_lv)
                with self.assertRaises(LevelUpError):
                    # level up past promotion level; this fails
                    morph.level_up(1)
                morph.promo_cls = promo_cls
                actual1 = morph.get_promotion_item()
                self.assertEqual(actual1, expected1)
                # promote
                morph.promote()
                # level is reset to 1
                self.assertEqual(morph.current_lv, 1)
                actual2 = morph.get_promotion_item()
                expected2 = promotion_item
                self.assertEqual(actual2, expected2)
                # level up to 20
                morph.level_up(19)
                with self.assertRaises(LevelUpError):
                    # level up past 20; this fails
                    morph.level_up(1)
                morph.promo_cls = promo_cls2
                actual3 = morph.get_promotion_item()
                expected3 = promotion_item
                self.assertEqual(actual3, expected3)
                # final promotion
                morph.promote()
                # level to 20
                morph.level_up(19)
                actual4 = morph.get_promotion_item()
                self.assertIsNone(actual4)
                with self.assertRaises(LevelUpError):
                    # level up past 20; this fails
                    morph.level_up(1)
                with self.assertRaises(PromotionError) as err_ctx:
                    morph.promote()
                (err_msg,) = err_ctx.exception.args
                self.assertIn("no available promotions", err_msg)


    def test_get_promotion_item__promotables(self):
        """
        """
        promotables = self._get_promotables(can_promote=True)
        promoitem_dict = {
            'Eirika': "Lunar Brace",
            #'Seth',
            'Franz': "Knight Crest",
            'Gilliam': "Knight Crest",
            'Vanessa': "Elysian Whip",
            'Moulder': "Guiding Ring",
            #'Ross': None,
            'Garcia': "Hero Crest",
            'Neimi': "Orion's Bolt",
            'Colm': "Ocean Seal",
            'Artur': "Guiding Ring",
            'Lute': "Guiding Ring",
            'Natasha': "Guiding Ring",
            'Joshua': "Hero Crest",
            'Ephraim': "Solar Brace",
            'Forde': "Knight Crest",
            'Kyle': "Knight Crest",
            #'Orson',
            'Tana': "Elysian Whip",
            #'Amelia',
            #'Innes',
            'Gerik': "Hero Crest",
            #'Tethys',
            'Marisa': "Hero Crest",
            "L'Arachel": "Guiding Ring",
            #'Dozla',
            #'Saleh',
            #'Ewan',
            'Cormag': "Elysian Whip",
            #'Rennac',
            #'Duessel',
            'Knoll': "Guiding Ring",
            #'Myrrh',
            #'Syrene',
            #'Caellach',
            #'Riev',
            #'Ismaire',
            #'Selena',
            #'Glen',
            #'Hayden',
            #'Valter',
            #'Fado',
            #'Lyon',
        }
        #trainees = ("Ross", "Amelia", "Ewan")
        #for name in filter(lambda name_: name_ not in trainees, promotables):
        for name in filter(lambda name_: name_ in promoitem_dict, promotables):
            morph = Morph8(name)
            #logger.debug("Getting promo-item for: '%s'", name)
            actual = morph.get_promotion_item()
            expected = promoitem_dict.pop(name)
            logger.debug("Promo-item for '%s' is: '%s'", name, actual)
            self.assertEqual(actual, expected)
            # extra
            morph.level_up(20 - morph.current_lv)
            try:
                morph.promote()
            except PromotionError:
                morph.promo_cls = morph.possible_promotions[0]
                morph.promote()
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)

    def test_get_promotion_item__nonpromotables(self):
        """
        """
        nonpromotables = self._get_promotables(can_promote=False)
        #expected = None
        for name in nonpromotables:
            morph = Morph8(name)
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)

    def test_as_string(self):
        """
        """
        morph = Morph8("Ewan")
        morph.use_metiss_tome()
        actual = morph.as_string()
        self.assertIsInstance(actual, str)
        logger.debug("as_string -> %s", actual)

    def test_inventory_size(self):
        """
        """
        morph = Morph8("Ephraim")
        actual = morph.inventory_size
        self.assertIsInstance(actual, int)
        self.assertGreater(actual, 0)

    def test_eirika__early_promotion(self):
        """
        """
        name = "Eirika"
        morph = Morph8(name)
        self.assertLess(morph.current_lv, 10)
        morph.promote()
        self.assertEqual(morph.current_clstype, "classes__promotion_gains")
        with self.assertRaises(PromotionError):
            morph.promote()

    def test_ephraim__early_promotion(self):
        """
        """
        name = "Ephraim"
        morph = Morph8(name)
        self.assertLess(morph.current_lv, 10)
        morph.promote()
        self.assertEqual(morph.current_clstype, "classes__promotion_gains")
        with self.assertRaises(PromotionError):
            morph.promote()

    def test_ross(self):
        """
        """
        name = "Ross"
        self._test_scrub(name)

    def test_amelia(self):
        """
        """
        name = "Amelia"
        self._test_scrub(name)

    def test_ewan(self):
        """
        """
        name = "Ewan"
        self._test_scrub(name)

    def _test_scrub(self, name):
        """
        """
        _morph = Morph8(name)
        _morph.current_lv = 10
        try:
            _morph.promote()
        except PromotionError as error:
            actual = error.reason
            expected = PromotionError.Reason.INVALID_PROMOTION
            self.assertEqual(actual, expected)
        promo_dict = {}
        # compile list of promotions
        for promo_cls in _morph.possible_promotions:
            morph = Morph8(name)
            morph.current_lv = 10
            morph.promo_cls = promo_cls
            morph.promote()
            morph.current_lv = 10
            try:
                morph.promote()
            except PromotionError as error:
                actual = error.reason
                expected = PromotionError.Reason.INVALID_PROMOTION
                self.assertEqual(actual, expected)
            promo_dict[promo_cls] = morph.possible_promotions
        for promo_cls, promoclasses2 in promo_dict.items():
            for promo_cls2 in promoclasses2:
                morph = Morph8(name)
                # try to promote at base level; this fails
                with self.assertRaises(PromotionError) as exc_ctx:
                    morph.promote()
                actual = exc_ctx.exception.reason
                expected = PromotionError.Reason.LEVEL_TOO_LOW
                self.assertEqual(actual, expected)
                # level up to promotion level
                morph.level_up(10 - morph.current_lv)
                with self.assertRaises(LevelUpError):
                    # level up past promotion level; this fails
                    morph.level_up(1)
                # promote
                morph.promo_cls = promo_cls
                morph.promote()
                # level is reset to 1
                self.assertEqual(morph.current_lv, 1)
                # level up to 20
                morph.level_up(19)
                with self.assertRaises(LevelUpError):
                    # level up past 20; this fails
                    morph.level_up(1)
                morph.promo_cls = promo_cls2
                # final promotion
                morph.promote()
                # level to 20
                morph.level_up(19)
                with self.assertRaises(LevelUpError):
                    # level up past 20; this fails
                    morph.level_up(1)
                with self.assertRaises(PromotionError) as err_ctx:
                    morph.promote()
                (err_msg,) = err_ctx.exception.args
                self.assertIn("no available promotions", err_msg)

    def test_nonpromotables(self):
        """
        """
        nonpromotables = self._get_promotables(False)
        for name in nonpromotables:
            logger.debug("Morph8(%r)", name)
            morph = Morph8(name)
            with self.assertRaises(PromotionError) as exc_ctx:
                morph.promote()
            actual = exc_ctx.exception.reason
            expected = PromotionError.Reason.NO_PROMOTIONS
            self.assertEqual(actual, expected)
            morph.level_up(20 - morph.current_lv)
            with self.assertRaises(LevelUpError):
                morph.level_up(1)
            with self.assertRaises(PromotionError) as err_ctx:
                morph.promote()
            expected = err_ctx.exception.reason
            actual = PromotionError.Reason.NO_PROMOTIONS
            self.assertEqual(actual, expected)

    def test_promotables(self):
        """
        """
        promotables = self._get_promotables(True)
        for name in filter(lambda name: name not in self.trainees, promotables):
            logger.debug("Morph8(%r)", name)
            morph = Morph8(name)
            morph.level_up(20 - morph.current_lv)
            try:
                morph.promote()
                morph.level_up(19)
                with self.assertRaises(LevelUpError):
                    morph.level_up(1)
                with self.assertRaises(PromotionError) as err_ctx:
                    morph.promote()
                expected = err_ctx.exception.reason
                actual = PromotionError.Reason.NO_PROMOTIONS
                self.assertEqual(actual, expected)
            except PromotionError:
                for promo_cls in morph.possible_promotions:
                    morph = Morph8(name)
                    morph.level_up(20 - morph.current_lv)
                    morph.promo_cls = promo_cls
                    morph.promote()
                    morph.level_up(19)
                    with self.assertRaises(LevelUpError):
                        morph.level_up(1)
                    with self.assertRaises(PromotionError) as err_ctx:
                        morph.promote()
                    expected = err_ctx.exception.reason
                    actual = PromotionError.Reason.NO_PROMOTIONS
                    self.assertEqual(actual, expected)

    def test_stat_boosters(self):
        """
        """
        item_bonus_dict = {
            "Angelic Robe": ("HP", 7),
            "Energy Ring": ("Pow", 2),
            "Secret Book": ("Skl", 2),
            "Speedwings": ("Spd", 2),
            "Goddess Icon": ("Lck", 2),
            "Dragonshield": ("Def", 2),
            "Talisman": ("Res", 2),
            "Boots": ("Mov", 2),
            "Body Ring": ("Con", 3),
        }
        morph = Morph8("Eirika")
        for item, statbonus in item_bonus_dict.items():
            original_stats = morph.current_stats.copy()
            morph.use_stat_booster(item)
            stat, bonus = statbonus
            expected = getattr(original_stats, stat) + bonus
            actual = getattr(morph.current_stats, stat)
            self.assertEqual(actual, expected)

    def test_metiss_tome(self):
        """
        """
        ewan = Morph8("Ewan")
        ewan.use_metiss_tome()
        ewan2 = Morph8("Ewan")
        diff = (ewan.growth_rates - ewan2.growth_rates)
        self.assertSetEqual(set(diff), {5})
        with self.assertRaises(GrowthsItemError) as err_ctx:
            ewan.use_metiss_tome()
        actual = err_ctx.exception.reason
        expected = GrowthsItemError.Reason.ALREADY_CONSUMED
        self.assertEqual(actual, expected)

    def test_inventory_size(self):
        """
        """
        lord = Morph8("Eirika")
        actual = lord.inventory_size
        expected = 5
        self.assertEqual(actual, expected)

class Morph9Tests(unittest.TestCase):
    """
    """

    def tearDown(self):
        """
        """
        logger.critical("%s", self.id())

    def setUp(self):
        """
        """
        logger.critical("%s", self.id())
        self.jill = Morph9("Jill")
        self.bands = (
            "Sword Band",
            "Soldier Band",
            "Fighter Band",
            "Archer Band",
            "Knight Band",
            "Paladin Band",
            "Pegasus Band",
            "Wyvern Band",
            "Mage Band",
            "Priest Band",
            "Thief Band",
            #"Knight Ward",
        )

    def test_inventory_size(self):
        """
        """
        morph = Morph9("Ike")
        actual = morph.inventory_size
        self.assertIsInstance(actual, int)
        self.assertGreater(actual, 0)

    def test_ike_can_promote_at_lv1(self):
        """
        """
        morph = Morph9("Ike")
        morph.promote()

    def test_volke_can_promote_at_base_lv(self):
        """
        """
        morph = Morph9("Volke")
        morph.promote()

    @staticmethod
    def _get_promotables(can_promote):
        """
        """
        # query for list of units who cannot promote
        url_name = "path-of-radiance"
        return _get_promotables(url_name, can_promote=can_promote)

    def test_get_promotion_item__ike(self):
        """
        """
        # ike
        name = "Ike"
        morph = Morph9(name)
        actual = morph.get_promotion_item()
        expected = "*Chapter 18 - Start*"
        self.assertEqual(actual, expected)
        morph.promote()
        actual = morph.get_promotion_item()
        self.assertIsNone(actual)

    def test_get_promotion_item__volke(self):
        """
        """
        # volke
        name = "Volke"
        morph = Morph9(name)
        actual = morph.get_promotion_item()
        expected = "*Chapter 19 - Pay Volke*"
        self.assertEqual(actual, expected)
        morph.promote()
        actual = morph.get_promotion_item()
        self.assertIsNone(actual)

    def test_get_promotion_item__promotables(self):
        """
        """
        promotables = self._get_promotables(can_promote=True)
        expected = "Master Seal"
        for name in filter(lambda name_: name_ not in ("Volke", "Ike"), promotables):
            morph = Morph9(name)
            actual = morph.get_promotion_item()
            logger.debug("Promo-item for '%s' is: '%s'", name, actual)
            #expected = promoitem_dict.pop(name)
            self.assertEqual(actual, expected)
            # extra
            morph.level_up(20 - morph.current_lv)
            morph.promote()
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)

    def test_get_promotion_item__nonpromotables(self):
        """
        """
        nonpromotables = self._get_promotables(can_promote=False)
        #expected = None
        for name in nonpromotables:
            morph = Morph9(name)
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)


    def test_promotables(self):
        """
        """
        promotables = self._get_promotables(True)
        for name in promotables:
            logger.debug("Morph9(%r)", name)
            morph = Morph9(name)
            morph.level_up(20 - morph.current_lv)
            morph.promote()
            morph.level_up(19)
            with self.assertRaises(LevelUpError):
                morph.level_up(1)
            with self.assertRaises(PromotionError) as err_ctx:
                morph.promote()
            expected = err_ctx.exception.reason
            actual = PromotionError.Reason.NO_PROMOTIONS
            self.assertEqual(actual, expected)

    def test_nonpromotables(self):
        """
        """
        nonpromotables = self._get_promotables(False)
        for name in nonpromotables:
            logger.debug("Morph9(%r)", name)
            morph = Morph9(name)
            with self.assertRaises(PromotionError) as exc_ctx:
                morph.promote()
            actual = exc_ctx.exception.reason
            expected = PromotionError.Reason.NO_PROMOTIONS
            self.assertEqual(actual, expected)
            morph.level_up(20 - morph.current_lv)
            with self.assertRaises(LevelUpError):
                morph.level_up(1)
            with self.assertRaises(PromotionError) as err_ctx:
                morph.promote()
            expected = err_ctx.exception.reason
            actual = PromotionError.Reason.NO_PROMOTIONS
            self.assertEqual(actual, expected)

    def test_stat_boosters(self):
        """
        """
        item_bonus_dict = {
            "Seraph Robe": ("HP", 7),
            "Energy Drop": ("Str", 2),
            "Spirit Dust": ("Mag", 2),
            "Secret Book": ("Skl", 2),
            "Speedwing": ("Spd", 2),
            "Ashera Icon": ("Lck", 2),
            "Dracoshield": ("Def", 2),
            "Talisman": ("Res", 2),
            "Boots": ("Mov", 2),
            "Body Ring": ("Con", 3),
        }
        morph = Morph9("Ike")
        for item, statbonus in item_bonus_dict.items():
            original_stats = morph.current_stats.copy()
            morph.use_stat_booster(item)
            stat, bonus = statbonus
            expected = getattr(original_stats, stat) + bonus
            actual = getattr(morph.current_stats, stat)
            self.assertEqual(actual, expected)

    def test_equip_knight_ward__not_a_knight(self):
        """
        """
        ike = Morph9("Ike")
        with self.assertRaises(KnightWardError) as err_ctx:
            ike.equip_knight_ward()
        actual = err_ctx.exception.reason
        expected = KnightWardError.Reason.NOT_A_KNIGHT
        self.assertEqual(actual, expected)

    def test_inventory_size(self):
        """
        """
        kieran = Morph9("Kieran")
        actual = kieran.inventory_size
        expected = 8
        self.assertEqual(actual, expected)

    def test_equip_knight_ward__no_space(self):
        """
        """
        # initialize
        kieran = Morph9("Kieran")
        inventory_size = kieran.inventory_size
        kieran.equipped_bands.update({i: None for i in range(inventory_size)})
        with self.assertRaises(KnightWardError) as err_ctx:
            kieran.equip_knight_ward()
        actual = err_ctx.exception.reason
        expected = KnightWardError.Reason.NO_INVENTORY_SPACE
        logger.debug("Actual: %s (%s)", actual, type(actual))
        logger.debug("Expected: %s (%s)", expected, type(expected))
        self.assertEqual(actual, expected)

    def test_unequip_knight_ward__not_a_knight(self):
        """
        """
        morph = Morph9("Ike")
        with self.assertRaises(KnightWardError):
            morph.unequip_knight_ward()

    def test_unequip_knight_ward(self):
        """
        """
        morph = Morph9("Oscar")
        with self.assertRaises(KnightWardError):
            morph.unequip_knight_ward()
        morph.equipped_bands = {"Knight Ward": None}
        morph.knight_ward_is_equipped = True
        morph.unequip_knight_ward()
        actual = morph.knight_ward_is_equipped
        self.assertIs(actual, False)
        actual = morph.equipped_bands
        self.assertDictEqual(actual, {})
        self.assertEqual(morph.growth_rates, morph._og_growth_rates)

    def test_equip_knight_ward(self):
        """
        """
        # initialize
        kieran = Morph9("Kieran")
        # assess state
        actual = kieran.knight_ward_is_equipped
        expected = False
        self.assertIs(actual, expected)
        # attempt to unequip Knight Ward.
        with self.assertRaises(KnightWardError) as err_ctx:
            kieran.unequip_knight_ward()
        actual = err_ctx.exception.reason
        expected = KnightWardError.Reason.NOT_EQUIPPED
        self.assertEqual(actual, expected)
        # save growths
        og_growths = kieran.growth_rates.copy()
        # equip knight ward
        kieran.equip_knight_ward()
        with self.assertRaises(KnightWardError) as err_ctx:
            kieran.equip_knight_ward()
        # check state
        actual = kieran.knight_ward_is_equipped
        expected = True
        self.assertIs(actual, expected)
        actual = err_ctx.exception.reason
        expected = KnightWardError.Reason.ALREADY_EQUIPPED
        self.assertEqual(actual, expected)
        # compare growths
        new_growths = kieran.growth_rates
        comparison = new_growths - og_growths
        actual = comparison.Spd
        expected = 30
        self.assertEqual(actual, expected)
        comparison.Spd = 0
        self.assertIs(all(comparison == kieran.Stats(**kieran.Stats.get_stat_dict(0))), True)

    def test_band_level_up(self):
        """
        """
        jill = self.jill
        bands = self.bands
        for i in range(3):
            band = bands[i]
            jill.equip_band(band)
        jill.unequip_band(band)
        with self.assertRaises(BandError) as err_ctx:
            jill.unequip_band("")
        actual = err_ctx.exception.reason
        expected = BandError.Reason.NOT_EQUIPPED
        self.assertEqual(actual, expected)
        first_band = bands[0]
        with self.assertRaises(BandError) as err_ctx:
            jill.equip_band(first_band)
        actual = err_ctx.exception.reason
        expected = BandError.Reason.ALREADY_EQUIPPED
        self.assertEqual(actual, expected)
        with self.assertRaises(BandError) as err_ctx:
            jill.equip_band("")
        actual = err_ctx.exception.reason
        expected = BandError.Reason.NOT_FOUND
        self.assertEqual(actual, expected)
        jill.level_up(10)
        jill2 = Morph5("Eda")
        jill2.level_up(10)

    def test_equip_band(self):
        """
        """
        band_name = self.bands[0]
        og_growths = self.jill.growth_rates.copy()
        self.jill.equip_band(band_name)
        self.assertIn(band_name, self.jill.equipped_bands)
        self.assertEqual(len(self.jill.equipped_bands), 1)
        new_growths = self.jill.growth_rates
        actual = all(og_growths == new_growths)
        expected = False
        self.assertIs(actual, expected)
        with self.assertRaises(BandError) as err_ctx:
            self.jill.equip_band(band_name)
        actual = err_ctx.exception.reason
        expected = BandError.Reason.ALREADY_EQUIPPED
        self.assertEqual(actual, expected)

    def test_equip_band__exceed_inventory_space(self):
        """
        """
        # equip bands
        jill = self.jill
        for i in range(8):
            band_name = self.bands[i]
            jill.equip_band(band_name)
        # affirm size of equipped bands
        self.assertGreater(len(self.bands), len(jill.equipped_bands))
        logger.debug("Equipped bands: '%s'", jill.equipped_bands.keys())
        # try to equip another band
        last_band = self.bands[-1]
        logger.debug("Trying to equip: '%s'", last_band)
        self.assertNotIn(last_band, jill.equipped_bands)
        with self.assertRaises(BandError) as err_ctx:
            jill.equip_band(last_band)
        actual = err_ctx.exception.reason
        expected = BandError.Reason.NO_INVENTORY_SPACE
        logger.debug("Actual: %s (%s)", actual, type(actual))
        logger.debug("Expected: %s (%s)", expected, type(expected))
        self.assertEqual(actual, expected)

    def test_equip_band__band_dne(self):
        """
        """
        band_name = ""
        og_growths = self.jill.growth_rates.copy()
        with self.assertRaises(BandError) as err_ctx:
            self.jill.equip_band(band_name)
        # check error
        actual = err_ctx.exception.reason
        expected = BandError.Reason.NOT_FOUND
        self.assertEqual(actual, expected)
        # check state
        self.assertNotIn(band_name, self.jill.equipped_bands)
        self.assertEqual(len(self.jill.equipped_bands), 0)
        new_growths = self.jill.growth_rates
        actual = all(og_growths == new_growths)
        expected = True
        self.assertIs(actual, expected)


class MorphFunctionTests(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        logger.debug("%s", self.id())
        self.lords_and_games = {
            1: "Marth",
            2: "Alm",
            3: "Marth",
            4: "Sigurd",
            5: "Leaf",
            6: "Roy",
            7: "Eliwood",
            8: "Ephraim",
            9: "Ike",
            10: "Micaiah",
            11: "Marth",
            12: "Marth",
            13: "Chrom",
            14: "Corrin",
            15: "Celica",
            16: "Byleth",
            17: "Alear",
        }

    def test_get_morph__roy(self):
        """
        """
        roy = get_morph(6, "Roy")
        actual = "Roy"
        expected = roy.name
        self.assertEqual(actual, expected)

    def test_get_morph__error_propagated_from_morph(self):
        """
        """
        with self.assertRaises(UnitNotFoundError) as err_ctx:
            get_morph(6, "Marth")
        actual = err_ctx.exception.unit_type
        expected = UnitNotFoundError.UnitType.NORMAL
        self.assertEqual(actual, expected)

    def test_get_morph__invalid_game(self):
        """
        """
        lords_and_games = self.lords_and_games
        for game_no in range(4, 10):
            lords_and_games.pop(game_no)
        for game, lord in lords_and_games.items():
            with self.assertRaises(NotImplementedError):
                get_morph(game, lord)

    def test_repr(self):
        """
        """
        for game_no in range(4, 10):
            lord = self.lords_and_games[game_no]
            morph = get_morph(game_no, lord)
            logger.debug("\n\n%s\n", morph)

    def test_repr__gba_promoted(self):
        """
        """
        for game_no in range(6, 9):
            lord = self.lords_and_games[game_no]
            morph = get_morph(game_no, lord)
            morph.use_stat_booster("Energy Ring")
            morph.level_up(20 - morph.current_lv)
            morph.promote()
            morph.use_stat_booster("Angelic Robe")
            logger.debug("\n\n%s\n", morph)

    def test_repr__lyn_mode(self):
        """
        """
        morph = get_morph(7, "Florina", lyn_mode=True)
        morph.level_up(20 - morph.current_lv)
        morph.promote()
        logger.debug("\n\n%s\n", morph)

    def test_repr__trainee(self):
        """
        """
        morph = get_morph(8, "Amelia")
        morph.level_up(10 - morph.current_lv)
        morph.promo_cls = "Cavalier (F)"
        morph.promote()
        morph.level_up(20 - morph.current_lv)
        morph.promo_cls = "Paladin (F)"
        morph.promote()
        logger.debug("\n\n%s\n", morph)

    def test_repr__gba_hard_mode(self):
        """
        """
        rutger = get_morph(6, "Rutger", hard_mode=True)
        rutger.level_up(20 - rutger.current_lv)
        rutger.promote()
        logger.debug("\n\n%s\n", rutger)

    def test_as_string__gba_growths_item(self):
        """
        """
        heath = get_morph(7, "Heath", hard_mode=True)
        heath.use_afas_drops()
        heath.level_up(20 - heath.current_lv)
        heath.promote()
        heath.use_stat_booster("Speedwings")
        logger.debug("\n\n%s\n", heath.as_string())

    def test_repr__genealogy_kid(self):
        """
        """
        larcei = get_morph(4, "Lakche", father="Lex")
        larcei.level_up(20 - larcei.current_lv)
        larcei.promote()
        logger.debug("\n\n%s\n", larcei)

    def test_repr__thracia_unit_with_scroll(self):
        """
        """
        asvel = get_morph(5, "Asvel")
        asvel.level_up(20 - asvel.current_lv)
        asvel.equip_scroll("Blaggi")
        asvel.equip_scroll("Odo")
        logger.debug("\n\n%s\n", asvel)

    def test_repr__radiant_unit_with_band(self):
        """
        """
        morph = get_morph(9, "Oscar")
        morph.equip_band("Thief Band")
        morph.equip_knight_ward()
        morph.level_up(20 - morph.current_lv)
        logger.debug("\n\n%s\n", morph)

    def test_repr__early_promo_lord(self):
        """
        """
        morph = get_morph(7, "Hector")
        #morph.level_up(20 - morph.current_lv)
        morph.promote()
        logger.debug("\n\n%s\n", morph)

    def test_gt__christmas_cavaliers(self):
        """
        """
        morph1 = Morph6("Allen")
        morph2 = Morph6("Lance")
        actual = (morph1 > morph2).__str__()
        logger.debug("\n\n%s\n", actual)

    def test_gt__hm_and_nonhm(self):
        """
        """
        morph1 = Morph6("Rutger", hard_mode=True)
        morph2 = Morph6("Marcus")
        actual = (morph1 > morph2).__str__()
        logger.debug("\n\n%s\n", actual)

    def test_gt__genealogykid_and_adult(self):
        """
        """
        morph1 = Morph4("Lakche", father="Lex")
        morph2 = Morph4("Sigurd")
        actual = (morph1 > morph2).__str__()
        logger.debug("\n\n%s\n", actual)

