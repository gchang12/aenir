"""
"""

import sqlite3
import unittest
from unittest.mock import patch
import enum
import logging
import json

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
    RadiantStats,
)

from aenir.logging import (
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
            "History": [],
            "Hard Mode": False,
            "Stat Boosters": [],
        }
        self.assertDictEqual(
            actual, expected,
        )

    def test_init__unit_dne(self):
        """
        """
        with self.assertRaises(ValueError) as assert_ctx:
            marth = self.TestMorph("Marth", which_bases=0, which_growths=0)
        (err_msg,) = assert_ctx.exception.args
        self.assertIn("%r" % (tuple(self.TestMorph.CHARACTER_LIST()),), err_msg)

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
        item = ""
        with self.assertRaises(KeyError):
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
        valid_promotions = ('Fighter', 'Pirate', 'Journeyman (2)')
        with self.assertRaises(KeyError) as key_ctx:
            ross.promote()
        (err_msg,) = key_ctx.exception.args
        self.assertIn(str(valid_promotions), err_msg)

class Morph4Tests(unittest.TestCase):
    """
    """

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
        self.assertIn("%r" % (tuple(father_list),), err_msg)
        logger.debug("%s", father_list)

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
            with self.assertRaises(ValueError):
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
            with self.assertRaises(ValueError):
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
                with self.assertRaises(ValueError):
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
                with self.assertRaises(ValueError):
                    morph.level_up(1)

class Morph5Tests(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        logger.critical("%s", self.id())

    @staticmethod
    def _get_promotables(can_promote):
        """
        """
        # query for list of units who cannot promote
        url_name = "thracia-776"
        return _get_promotables(url_name, can_promote=can_promote)

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
            with self.assertRaises(ValueError):
                morph.level_up(1)

    def test_nonpromotables(self):
        """
        """
        nonpromotables = self._get_promotables(can_promote=False)
        logger.debug("%s", nonpromotables)
        for name in nonpromotables:
            morph = Morph5(name)
            morph.level_up(20 - morph.current_lv)
            with self.assertRaises(ValueError):
                morph.level_up(1)

    def test_lara__long_path(self):
        """
        """
        # Thief -> Thief Fighter -> Dancer -> Thief Fighter
        lara = Morph5("Lara")
        lara.level_up(10 - lara.current_lv)
        with self.assertRaises(KeyError) as err_ctx:
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
        with self.assertRaises(ValueError):
            lara.promote()
        #logger.debug("%s", err_ctx.exception.args)

    def test_lara__short_path(self):
        """
        """
        # Thief -> Dancer -> Thief Fighter
        lara = Morph5("Lara")
        lara.promo_cls ="Dancer"
        lara.promote()
        with self.assertRaises(ValueError):
            lara.promote()
        lara.level_up(9)
        lara.promote()
        with self.assertRaises(ValueError):
            lara.promote()

    def test_scroll_level_up(self):
        """
        """
        eda = Morph5("Eda")
        eda.equip_scroll("Blaggi")
        eda.equip_scroll("Heim")
        eda.equip_scroll("Fala")
        eda.unequip_scroll("Fala")
        with self.assertRaises(KeyError):
            eda.unequip_scroll("")
        with self.assertRaises(ValueError):
            eda.equip_scroll("Heim")
        eda.level_up(10)
        eda2 = Morph5("Eda")
        eda2.level_up(10)
        self.assertEqual(eda.current_stats.Str - eda2.current_stats.Str, -1)
        self.assertEqual(eda.current_stats.Mag - eda2.current_stats.Mag, 4)
        self.assertEqual(eda.current_stats.Lck - eda2.current_stats.Lck, 4)
        self.assertEqual(eda.current_stats.Def - eda2.current_stats.Def, -1)

class Morph6Tests(unittest.TestCase):
    """
    """

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

    def test_hugh(self):
        """
        """
        hugh = Morph6("Hugh")
        hugh.decline_hugh()
        hugh.decline_hugh()
        hugh.decline_hugh()
        with self.assertRaises(ValueError):
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
        roy = Morph6("Roy")
        self.assertEqual(roy.current_lv, 1)
        roy.promote()
        self.assertEqual(roy.current_cls, "Master Lord")

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
            with self.assertRaises(ValueError):
                morph.level_up(1)
            with self.assertRaises(ValueError):
                morph.promote()

    def test_nonpromotables(self):
        """
        """
        nonpromotables = self._get_promotables(False)
        for name in nonpromotables:
            hard_mode = " (HM)" in name
            name = name.replace(" (HM)", "")
            logger.debug("Morph6(%r, hard_mode=%r)", name, hard_mode)
            morph = Morph6(name, hard_mode=hard_mode)
            with self.assertRaises(ValueError):
                morph.promote()
            morph.level_up(20 - morph.current_lv)
            #morph.promote()
            #morph.level_up(19)
            with self.assertRaises(ValueError):
                morph.level_up(1)

class Morph7Tests(unittest.TestCase):
    """
    """

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

    def test_afas_drops(self):
        """
        """
        nino = Morph7("Nino")
        nino.use_growths_item()
        nino2 = Morph7("Nino")
        diff = (nino.growth_rates - nino2.growth_rates).as_dict()
        self.assertSetEqual(set(diff.values()), {5, None})

    def test_no_hardmode_version(self):
        """
        """
        with self.assertLogs(logger, logging.WARNING):
            matthew = Morph7("Matthew", hard_mode=True)
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
        with self.assertRaises(ValueError):
            wallace.promote()
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
            with self.assertRaises(ValueError):
                morph.level_up(1)
            with self.assertRaises(ValueError):
                morph.promote()

    def test_nonpromotables(self):
        """
        """
        nonpromotables = self._get_promotables(False)
        for name in filter(lambda name: name not in self.lyndis_league, nonpromotables):
            hard_mode = " (HM)" in name
            name = name.replace(" (HM)", "")
            logger.debug("Morph7(%r, hard_mode=%r)", name, hard_mode)
            morph = Morph7(name, hard_mode=hard_mode)
            with self.assertRaises(ValueError):
                morph.promote()
            morph.level_up(20 - morph.current_lv)
            with self.assertRaises(ValueError):
                morph.level_up(1)
            with self.assertRaises(ValueError):
                morph.promote()

class Morph8Tests(unittest.TestCase):
    """
    """

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
        except KeyError:
            pass
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
            except KeyError:
                pass
            promo_dict[promo_cls] = morph.possible_promotions
        for promo_cls, promoclasses2 in promo_dict.items():
            for promo_cls2 in promoclasses2:
                morph = Morph8(name)
                # try to promote at base level; this fails
                with self.assertRaises(ValueError):
                    morph.promote()
                # level up to promotion level
                morph.level_up(10 - morph.current_lv)
                with self.assertRaises(ValueError):
                    # level up past promotion level; this fails
                    morph.level_up(1)
                # promote
                morph.promo_cls = promo_cls
                morph.promote()
                # level is reset to 1
                self.assertEqual(morph.current_lv, 1)
                # level up to 20
                morph.level_up(19)
                with self.assertRaises(ValueError):
                    # level up past 20; this fails
                    morph.level_up(1)
                morph.promo_cls = promo_cls2
                # final promotion
                morph.promote()
                # level to 20
                morph.level_up(19)
                with self.assertRaises(ValueError):
                    # level up past 20; this fails
                    morph.level_up(1)
                with self.assertRaises(ValueError) as err_ctx:
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
            with self.assertRaises(ValueError):
                morph.promote()
            morph.level_up(20 - morph.current_lv)
            with self.assertRaises(ValueError):
                morph.level_up(1)
            with self.assertRaises(ValueError):
                morph.promote()

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
                with self.assertRaises(ValueError):
                    morph.level_up(1)
                with self.assertRaises(ValueError):
                    morph.promote()
            except KeyError:
                for promo_cls in morph.possible_promotions:
                    morph = Morph8(name)
                    morph.level_up(20 - morph.current_lv)
                    morph.promo_cls = promo_cls
                    morph.promote()
                    morph.level_up(19)
                    with self.assertRaises(ValueError):
                        morph.level_up(1)
                    with self.assertRaises(ValueError):
                        morph.promote()

class Morph9Tests(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        logger.critical("%s", self.id())

    @staticmethod
    def _get_promotables(can_promote):
        """
        """
        # query for list of units who cannot promote
        url_name = "path-of-radiance"
        return _get_promotables(url_name, can_promote=can_promote)

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
            with self.assertRaises(ValueError):
                morph.level_up(1)
            with self.assertRaises(ValueError):
                morph.promote()

    def test_nonpromotables(self):
        """
        """
        nonpromotables = self._get_promotables(False)
        for name in nonpromotables:
            logger.debug("Morph9(%r)", name)
            morph = Morph9(name)
            with self.assertRaises(ValueError):
                morph.promote()
            morph.level_up(20 - morph.current_lv)
            with self.assertRaises(ValueError):
                morph.level_up(1)
            with self.assertRaises(ValueError):
                morph.promote()

