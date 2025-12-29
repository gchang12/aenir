"""
Defines functions to test Morph functionality.
"""

import sqlite3
import logging
import json
import unittest
from unittest.mock import patch
import importlib.resources

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
    Gets database-bound list of units who can be promoted.
    """
    # query for list of units who cannot promote
    table_name = "characters__base_stats-JOIN-classes__promotion_gains"
    path_to_db = f"src/aenir/static/{url_name}/cleaned_stats.db"
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

class NoGameMorph(unittest.TestCase):
    """
    Demonstrates behavior for Morph subclasses whose GAME methods haven't been implemented.
    """

    def setUp(self):
        """
        Defines Morph subclass without GAME method implementation.
        """
        class TestMorph(BaseMorph):
            """
            Morph subclass without GAME method implementation.
            """
        self.Morph = TestMorph
        logger.critical("%s", self.id())

    def test_GAME(self):
        """
        Asserts that calling `GAME` throws an error.
        """
        with self.assertRaises(NotImplementedError):
            self.Morph.GAME()

    def test_path_to__GAME_not_implemented(self):
        """
        Asserts that calling `path_to` throws an error.
        """
        with self.assertRaises(NotImplementedError):
            self.Morph.path_to("something")

class GamedMorph(unittest.TestCase):
    """
    Demonstrates behavior for Morph subclasses whose GAME methods have been implemented properly.
    """

    def setUp(self):
        """
        Defines Morph subclass with proper GAME method implementation.
        """
        class TestMorph6(BaseMorph):
            """
            Morph subclass with proper GAME method implementation.
            """
            @classmethod
            def GAME(cls):
                """
                Returns instance of .games.FireEmblemGame
                """
                return FireEmblemGame(6)
        self.Morph = TestMorph6
        self.kishuna = self.Morph()
        logger.critical("%s", self.id())

    def test_query_db__without_filters(self):
        """
        Demonstrates that one can query db independent of `GAME` method return-value.
        """
        path_to_db = "src/aenir/static/binding-blade/cleaned_stats.db"
        table = "characters__base_stats0"
        fields = ("HP", "Def")
        filters = None
        with sqlite3.connect(path_to_db) as cnxn:
            cnxn.row_factory = sqlite3.Row
            expected = cnxn.execute(
                "SELECT HP, Def FROM characters__base_stats0;",
            )
        actual = self.Morph.query_db(
            path_to_db,
            table,
            fields,
            filters,
        )
        self.assertEqual(actual.fetchall(), expected.fetchall())

    def test_query_db__with_filters(self):
        """
        Demonstrates db-querying with filters.
        """
        path_to_db = "src/aenir/static/binding-blade/cleaned_stats.db"
        table = "characters__base_stats0"
        fields = ("Pow", "Spd")
        filters = {"Name": "Rutger"}
        with sqlite3.connect(path_to_db) as cnxn:
            cnxn.row_factory = sqlite3.Row
            expected = cnxn.execute(
                "SELECT Pow, Spd FROM characters__base_stats0 WHERE Name='Rutger';",
            )
        actual = self.Morph.query_db(
            path_to_db,
            table,
            fields,
            filters,
        )
        self.assertEqual(actual.fetchall(), expected.fetchall())

    def test_query_db__with_filters__no_results(self):
        """
        Demonstrates db-querying with null resultset.
        """
        path_to_db = "src/aenir/static/binding-blade/cleaned_stats.db"
        table = "characters__base_stats0"
        fields = ("Pow", "Spd")
        filters = {"Name": ""}
        with sqlite3.connect(path_to_db) as cnxn:
            cnxn.row_factory = sqlite3.Row
            expected = cnxn.execute(
                "SELECT Pow, Spd FROM characters__base_stats0 WHERE false;",
            )
        actual = self.Morph.query_db(
            path_to_db,
            table,
            fields,
            filters,
        )
        self.assertEqual(actual.fetchall(), expected.fetchall())

    @unittest.skip("No `inventory_size` attribute yet.")
    def test_inventory_size_is_zero(self):
        """
        Asserts inventory size is zero for games without scrolls or bands.
        """
        actual = self.Morph.GAME().value
        expected = 7 # ie, Blazing Sword
        self.assertEqual(actual, expected)
        actual = self.kishuna.inventory_size
        expected = 0
        self.assertEqual(actual, expected)

    def test_query_db__fields_not_iterable(self):
        """
        Query db with non-iterable field.
        """
        path_to_db = "static/binding-blade/cleaned_stats.db"
        table = "characters__base_stats0"
        fields = None
        filters = {"Name": "Ruter"}
        with self.assertRaises(TypeError):
            self.Morph.query_db(
                path_to_db,
                table,
                fields,
                filters,
            )

    def test_query_db__filterset_has_no_items_method(self):
        """
        Demonstrates calling of db-query method with `filters` value that lacks `items` method.
        """
        path_to_db = "static/binding-blade/cleaned_stats.db"
        table = "characters__base_stats0"
        fields = ("Pow", "Spd")
        filters = [("Name", "Rutger")]
        with self.assertRaises(AttributeError):
            self.Morph.query_db(
                path_to_db,
                table,
                fields,
                filters,
            )

    def test_query_db__path_not_str(self):
        """
        Demonstrates calling of db-query method with non-str path.
        """
        path_to_db = None
        table = "characters__base_stats0"
        fields = ("Pow", "Spd")
        filters = {"Name": "Ruter"}
        with self.assertRaises(TypeError):
            self.Morph.query_db(
                path_to_db,
                table,
                fields,
                filters,
            )

    def test_query_db__table_dne(self):
        """
        Demonstrates calling of db-query method with nonexistent table.
        """
        path_to_db = "static/binding-blade/cleaned_stats.db"
        table = "characters__base_stats"
        fields = ("Pow", "Spd")
        filters = {"Name": "Ruter"}
        with self.assertRaises(sqlite3.OperationalError):
            self.Morph.query_db(
                path_to_db,
                table,
                fields,
                filters,
            )

    def test_path_to__file_is_not_string(self):
        """
        What happens when one tries to call `path_to` with a non-str argument.
        """
        with self.assertRaises(TypeError):
            self.Morph.path_to(None)

    def test_lookup(self):
        """
        Helper method to get right lookup keywords.
        """
        home_data = ("characters__base_stats", "Roy")
        target_data = ("classes__maximum_stats", "Class")
        tableindex = 0
        actual = self.kishuna.lookup(
            home_data,
            target_data,
            tableindex,
        )
        path_to_db = importlib.resources.files("aenir") / "static/binding-blade/cleaned_stats.db"
        expected = {
            "path_to_db": str(path_to_db),
            "table": "classes__maximum_stats0",
            "fields": ("HP", "Pow", "Skl", "Spd", "Lck", "Def", "Res", "Con", "Mov"),
            "filters": {"Class": "Non-promoted"},
        }
        self.assertDictEqual(actual, expected)
        # resultset is not None (check if 'query_db' is called)

    def test_lookup__bad_data_passed(self):
        """
        What happens when bad data is passed into the helper function.
        """
        home_data = ("characters__base_stats", "Roy", None)
        target_data = ("classes__maximum_stats", "Class")
        tableindex = 0
        with self.assertRaises(ValueError):
            self.kishuna.lookup(
                home_data,
                target_data,
                tableindex,
            )

    def test_lookup__json_file_dne(self):
        """
        What happens if the queried table does not exist.
        """
        home_data = ("characters__base_stats", "Roy")
        target_data = ("classes__maximum_stat", "Class")
        tableindex = 0
        with self.assertRaises(sqlite3.OperationalError):
            self.kishuna.lookup(
                home_data,
                target_data,
                tableindex,
            )

    @unittest.expectedFailure # You know, because sqlite3.Cursor is immutable and its attributes cannot be reset
    @patch("sqlite3.Cursor.fetchone")
    def test_lookup__aliased_value_is_none(self, MOCK_fetchone):
        """
        What happens when the column is null.
        """
        home_data = ("characters__base_stats", "Roy")
        target_data = ("classes__maximum_stats", "Class")
        tableindex = 0
        kishuna = self.Morph()
        MOCK_fetchone.return_value = {"Roy": None}
        actual = kishuna.lookup(
            home_data,
            target_data,
            tableindex,
        )
        self.assertIsNone(actual)
        # resultset is None

    def test_lookup__lookup_value_dne(self):
        """
        What happens when the value you're looking for DNE.
        """
        home_data = ("characters__base_stats", "Marth")
        target_data = ("classes__maximum_stats", "Class")
        tableindex = 0
        actual = self.kishuna.lookup(
            home_data,
            target_data,
            tableindex,
        )
        self.assertIsNone(actual)

    def test_query_db__more_than_one_filter_provided(self):
        """
        Demonstration of multi-filter invocation.
        """
        path_to_db = "src/aenir/static/binding-blade/cleaned_stats.db"
        table = "characters__growth_rates0"
        fields = ("Pow", "Spd")
        filters = {"Spd": 40, "Pow": 40}
        # should return Wendy, Wolt, and Roy.
        with sqlite3.connect(path_to_db) as cnxn:
            cnxn.row_factory = sqlite3.Row
            expected = cnxn.execute(
                'SELECT Pow, Spd FROM characters__growth_rates0 WHERE Spd=40 AND Pow=40;',
            )
        actual = self.Morph.query_db(
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

class BadGameMorph(unittest.TestCase):
    """
    Demonstrates calling of Morph subclass whose `GAME` method returns a value of the incorrect type.
    """

    def setUp(self):
        """
        Defines a Morph with a bad GAME method.
        """
        class TestMorphNoURLName(BaseMorph):
            """
            A subclass of BaseMorph that returns a bad `GAME` value. 
            """
            @staticmethod
            def GAME():
                """
                Lacks a `url_name` value.
                """
                return 4
        self.Morph = TestMorphNoURLName
        logger.critical("%s", self.id())

    def test_path_to(self):
        """
        Asserts that invocation of `path_to` fails because `GAME` returns something that lacks a `url_name` attribute.
        """
        with self.assertRaises(AttributeError):
            self.Morph.path_to("something")

class AllMorphs(unittest.TestCase):
    """
    Contains test-cases that encompass more than one Morph subclass.
    """

    def test_STATS(self):
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
                A Morph class whose `GAME` method returns a valid value.
                """
                @classmethod
                def GAME(cls):
                    """
                    """
                    return FireEmblemGame(game_no)
            expected = gameno_to_stats[game_no]
            actual = TestMorphWithGame.STATS()
            self.assertEqual(actual, expected)

    def test_promote__branched_promotion(self):
        """
        Promotion method encompasses branched promotion.
        """
        class TestMorph4(Morph):
            """
            FE4: Genealogy of the Holy War
            """
            #__name__ = "Morph"
            game_no = 4
            @classmethod
            def GAME(cls):
                """
                Affirms that this works.
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

    def test_get_true_character_list5(self):
        """
        Demonstrates that `get_true_character_list` works.
        """
        class Morph5(Morph):
            """
            Thracia 776
            """
            game_no = 5
        expected = Morph5.CHARACTER_LIST()
        actual = Morph5.get_true_character_list()
        self.assertEqual(tuple(actual), expected)

class Morph6Class2(unittest.TestCase):
    """
    Demonstrates Morph being subclassed properly.
    """

    def setUp(self):
        """
        Defines a usable subclass of 'Morph'
        """
        logger.critical("%s", self.id())
        class TestMorph6(Morph):
            """
            A virtual representation of a unit from FE6: Binding Blade.
            """
            game_no = 6

        self.Morph = TestMorph6
        self.Morph.__name__ = "Morph"
        self.init_kwargs = {
            "name": "Rutger",
            "which_bases": 0,
            "which_growths": 0,
        }
        self.kishuna = self.Morph(**self.init_kwargs)

    def test_as_string(self):
        """
        Prints str-representation to log-report.
        """
        morph = self.kishuna
        morph._use_stat_booster("Angelic Robe", {"Angelic Robe": ("HP", 7)})
        miscellany = [("Hard Mode", "True")]
        actual = morph._as_string(miscellany=miscellany, show_stat_boosters=True)
        logger.debug("as_string -> %s", actual)

    def test_as_string2(self):
        """
        Prints str-representation to log-report when miscellany=None
        """
        morph = self.kishuna
        morph._use_stat_booster("Angelic Robe", {"Angelic Robe": ("HP", 7)})
        miscellany = None
        actual = morph._as_string(miscellany=miscellany, show_stat_boosters=True)
        logger.debug("as_string -> %s", actual)

    def test_iter(self):
        """
        Asserts that iter returns list of growable stats and their values.
        """
        kwargs = self.init_kwargs
        multiplier = 100
        morph = self.kishuna
        _expected = [
            ("HP", 22),
            ("Pow", 7),
            ("Skl", 12),
            ("Spd", 13),
            ("Lck", 2),
            ("Def", 5),
            ("Res", 0),
        ]
        actual = []
        for statval in morph:
            actual.append(statval)
        expected = [numval * multiplier for (_, numval) in _expected]
        self.assertListEqual(actual, expected)

    def test_CHARACTER_LIST(self):
        """
        Validates list of all valid characters.
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
        actual = self.Morph.CHARACTER_LIST()
        self.assertTupleEqual(actual, expected)

    def test_set_max_level(self):
        """
        Checks `max_level` is set upon calling `set_max_level`
        """
        morph = self.kishuna
        self.assertIsNone(morph.max_level)
        morph._set_max_level()
        self.assertIsInstance(morph.max_level, int)

    def test_set_min_promo_level(self):
        """
        Checks `min_promo_level` is set upon calling `set_min_promo_level`
        """
        morph = self.kishuna
        self.assertIsNone(morph.min_promo_level)
        morph._set_min_promo_level()
        self.assertIsInstance(morph.min_promo_level, int)

    def test_init__unit_dne(self):
        """
        Asserts throwing of UnitDNE error if you try to look for a nonexistent unit.
        """
        with self.assertRaises(UnitNotFoundError) as assert_ctx:
            marth = self.Morph("Marth", which_bases=0, which_growths=0)
        (err_msg,) = assert_ctx.exception.args
        self.assertIn("%r" % (tuple(self.Morph.CHARACTER_LIST()),), err_msg)
        #actual = assert_ctx.exception.unit_type
        #expected = UnitNotFoundError.UnitType.NORMAL
        #self.assertEqual(actual, expected)

    def test_init__bad_bases_index(self):
        """
        What happens when you try to look for a table that DNE.
        """
        bad_bases = 99
        with self.assertRaises(sqlite3.OperationalError):
            self.Morph("Roy", which_bases=bad_bases, which_growths=0)
        bad_growths = 99
        with self.assertRaises(sqlite3.OperationalError):
            self.Morph("Roy", which_bases=0, which_growths=bad_growths)

class FE4Ayra(unittest.TestCase):
    """
    Conduct series of tests with FE4!Ayra as subject.
    """

    def setUp(self):
        """
        Initialize Morph4 instance for Lex!Lyra.
        """
        class TestMorph4(Morph):
            """
            FE4: Genealogy of the Holy War
            """
            #__name__ = "Morph"
            game_no = 4

            @classmethod
            def GAME(cls):
                """
                Confirms that this implementation doesn't crash the program.
                """
                return FireEmblemGame(cls.game_no)
        self.Morph = TestMorph4
        self.kishuna = TestMorph4("Ira", which_bases=0, which_growths=0)
        logger.critical("%s", self.id())

    def test_promote__branched_promotion(self):
        """
        Demo of pseudo-branched promotion working.
        """
        ira = self.kishuna
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
        base_ira = self.Morph("Ira", which_bases=0, which_growths=0)
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

class FE6Rutger(unittest.TestCase):
    """
    Defines a series of tests using Rutger as a test subject and a rudimentary Morph subclass.
    """

    def setUp(self):
        """
        Defines rudimentary Morph subclass and instance thereof also.
        """
        class TestMorph6(Morph):
            """
            A virtual representation of a unit from FE6: Binding Blade.
            """
            game_no = 6
        self.morph = TestMorph6("Rutger", which_bases=0, which_growths=0)
        logger.critical("%s", self.id())

    def test_init(self):
        """
        Demonstrates initialization of Morph instance.
        """
        rutger = self.morph
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

    def test_level_up(self):
        """
        Demonstrates that `level_up` works.
        """
        rutger = self.morph
        rutger.level_up(16)
        self.assertEqual(rutger.current_lv, 20)
        actual = rutger.current_stats
        expected = GBAStats(
            multiplier=1,
            HP=3480,
            Pow=1180,
            Skl=2000,
            Spd=2000,
            Lck=680,
            Def=820,
            Res=320,
            Con=700,
            Mov=500,
        )
        self.assertEqual(actual, expected)

    def test_level_up__level_too_high(self):
        """
        Demonstrates that `level_up` throws an error if the target level exceeds max.
        """
        rutger = self.morph
        with self.assertRaises(LevelUpError) as err_ctx:
            rutger.level_up(20)
        actual = rutger.current_lv
        expected = 4
        self.assertEqual(actual, expected)
        expected = [
            ("HP", 2200),
            ("Pow", 700),
            ("Skl", 1200),
            ("Spd", 1300),
            ("Lck", 200),
            ("Def", 500),
            ("Res", 0),
            ("Con", 700),
            ("Mov", 500),
        ]
        actual = rutger.current_stats.as_list()
        self.assertIs(actual, expected)

    def test_promote(self):
        """
        Demonstrates that `promote` works.
        """
        rutger = self.morph
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
        # bases + promo
        expected = [
            ("HP", 2200 + 500),
            ("Pow", 700 + 200),
            ("Skl", 1200 + 200),
            ("Spd", 1300 + 100),
            ("Lck", 200 + 0),
            ("Def", 500 + 300),
            ("Res", 0 + 200),
            ("Con", 700 + 100),
            ("Mov", 500 + 100),
        ]
        actual = rutger.current_stats.as_list()
        self.assertEqual(actual, expected)

    def test_stat_comparison_fail(self):
        """
        Asserts that stat comparison will fail because of bad stat.
        """
        rutger = self.morph
        rutger.current_stats.Mov = 9900 # This is what will cause the test to fail
        actual = rutger.current_stats.as_list()
        expected = [
            ("HP", 2200),
            ("Pow", 700),
            ("Skl", 1200),
            ("Spd", 1300),
            ("Lck", 200),
            ("Def", 500),
            ("Res", 0),
            ("Con", 700),
            ("Mov", 500),
        ]
        with self.assertRaises(AssertionError):
            self.assertListEqual(actual, expected)

    def test_promote__level_too_low(self):
        """
        What happens when it's not time to promote your unit.
        """
        rutger = self.morph
        #rutger.min_promo_level = 10
        with self.assertRaises(PromotionError) as exc_ctx:
            rutger.promote()
        err = exc_ctx.exception
        actual = err.reason
        expected = PromotionError.Reason.LEVEL_TOO_LOW
        self.assertEqual(actual, expected)
        actual = err.min_promo_level
        expected = rutger.min_promo_level
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
        base_rutger = self.Morph("Rutger", which_bases=0, which_growths=0)
        expected = base_rutger.current_stats
        actual = rutger.current_stats
        self.assertEqual(actual, expected)

    def test_promote__already_promoted(self):
        """
        What happens when the user has a promotable morph impersonate an unpromotable unit prior to promotion.
        """
        rutger = self.morph
        rutger._name = "Marcus"
        # do the thing.
        with self.assertRaises(PromotionError) as exc_ctx:
            rutger.promote()
        # validation of state
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
        # assert maxes are not those of Swordmaster
        unpromoted_maxes = [
            ("HP", 6000),
            ("Pow", 2000),
            ("Skl", 2000),
            ("Spd", 2000),
            ("Lck", 3000),
            ("Def", 2000),
            ("Res", 2000),
            ("Con", 2000),
            ("Mov", 1500),
        ]
        expected = unpromoted_maxes.as_list()
        actual = rutger.max_stats.as_list()
        self.assertListEqual(actual, expected)
        # assert that stats have not increased by expected amount.
        expected = [
            ("HP", 2200),
            ("Pow", 700),
            ("Skl", 1200),
            ("Spd", 1300),
            ("Lck", 200),
            ("Def", 500),
            ("Res", 0),
            ("Con", 700),
            ("Mov", 500),
        ]
        actual = rutger.current_stats.as_list()
        self.assertEqual(actual, expected)

class FE6Roy(unittest.TestCase):
    """
    Conducts tests with FE6!Roy as subject.
    """

    def setUp(self):
        """
        Initializes Morph of Roy.
        """
        class TestMorph6(Morph):
            """
            A virtual representation of a unit from FE6: Binding Blade.
            """
            game_no = 6
        self.morph = self.TestMorph6("Roy", which_bases=0, which_growths=0)
        logger.critical("%s", self.id())

    def test_use_stat_booster(self):
        """
        Demonstrates use of stat boosters.
        """
        roy = self.morph
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
            expected[stat] += bonus * 100
        roy.stat_boosters = item_bonus_dict
        for item in item_bonus_dict:
            roy._use_stat_booster(item, item_bonus_dict)
        actual = roy.current_stats.as_dict()
        self.assertDictEqual(actual, expected)

    def test_use_stat_booster__fail(self):
        """
        Demonstrates unsuccessful use of stat boosters.
        """
        roy = self.morph
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
            roy._use_stat_booster(item, item_bonus_dict)
        err = err_ctx.exception
        actual = err.reason
        expected = StatBoosterError.Reason.NOT_FOUND
        self.assertEqual(actual, expected)
        actual = err.valid_stat_boosters
        expected = item_bonus_dict
        self.assertEqual(actual, expected)


class Morph4TestCase(unittest.TestCase):
    """
    Defines helper methods for test-cases that subclass this.
    """

    @staticmethod
    def _get_promotables(can_promote):
        """
        Gets list of units who can be promoted.
        """
        # query for list of units who cannot promote
        url_name = "genealogy-of-the-holy-war"
        return _get_promotables(url_name, can_promote=can_promote)

    @staticmethod
    def _get_kid_list():
        """
        Gets list of child units.
        """
        # query for list of kids
        path_to_db = "src/aenir/static/genealogy-of-the-holy-war/cleaned_stats.db"
        with sqlite3.connect(path_to_db) as cnxn:
            cnxn.row_factory = sqlite3.Row
            resultset = [result["Name"] for result in cnxn.execute("SELECT Name FROM characters__base_stats1;").fetchall()]
        kid_list = sorted(set(resultset), key=lambda name: resultset.index(name))
        return kid_list

    @staticmethod
    def _get_father_list():
        """
        Gets list of father units.
        """
        # query for list of fathers
        path_to_db = "src/aenir/static/genealogy-of-the-holy-war/cleaned_stats.db"
        with sqlite3.connect(path_to_db) as cnxn:
            cnxn.row_factory = sqlite3.Row
            resultset = [result["Father"] for result in cnxn.execute("SELECT Father FROM characters__base_stats1;").fetchall()]
        father_list = sorted(set(resultset), key=lambda name: resultset.index(name))
        return father_list

    def setUp(self):
        """
        Prints test-id to log-report for demarcation.
        """
        logger.critical("%s", self.id())

class Morph4Class(Morph4TestCase):
    """
    Tests class methods and pre-initialization methods.
    """

    def test_bastard(self):
        """
        What happens when one tries to initialize a child unit without a father.
        """
        with self.assertRaises(InitError) as err_ctx:
            Morph4("Lakche", father="")
        # generate father list
        actual = err_ctx.exception.missing_value
        expected = InitError.MissingValue.FATHER
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
        err = err_ctx.exception
        (err_msg,) = err.args
        self.assertIn("%r" % (tuple(father_list),), err_msg)
        logger.debug("%s", father_list)
        actual = err.init_params
        expected = {"father": ('Arden', 'Azel', 'Alec', 'Claude', 'Jamka', 'Dew', 'Noish', 'Fin', 'Beowolf', 'Holyn', 'Midayle', 'Levin', 'Lex')}
        self.assertDictEqual(actual, expected)

    def test_init__father_specified_for_nonkid(self):
        """
        What happens when you try to specify a father for a non-child-unit.
        """
        with self.assertLogs(logger, logging.WARNING):
            Morph4("Sigurd", father="Lex")

    def test_CHILD_LIST(self):
        """
        Validates `CHILD_LIST`.
        """
        actual = Morph4.CHILD_LIST()
        expected = (
            'Rana',
            'Lakche',
            'Skasaher',
            'Delmud',
            'Lester',
            'Fee',
            'Arthur',
            'Patty',
            'Nanna',
            'Leen',
            'Tinny',
            'Faval',
            'Sety',
            'Corpul',
        )
        self.assertTupleEqual(actual, expected)

    def test_FATHER_LIST(self):
        """
        Validates `FATHER_LIST`.
        """
        actual = Morph4.FATHER_LIST()
        expected = (
            'Arden',
            'Azel',
            'Alec',
            'Claude',
            'Jamka',
            'Dew',
            'Noish',
            'Fin',
            'Beowolf',
            'Holyn',
            'Midayle',
            'Levin',
            'Lex',
        )
        self.assertTupleEqual(actual, expected)

class FE4Deirdre(Morph4TestCase):
    """
    Performs tests with Deirdre as test subject.
    """

    def setUp(self):
        """
        Initializes Deirdre Morph.
        """
        self.morph = Morph4("Diadora")
        super().setUp()

    def test_get_promotion_item__deirdre(self):
        """
        Asserts that Deirdre cannot promote.
        """
        deirdre = self.morph
        self.assertEqual(deirdre.max_level, 30)
        #with self.assertRaises(ValueError):
        actual = deirdre.get_promotion_item()
        self.assertIsNone(actual)

class FE4UnpromotedUnit(Morph4TestCase):
    """
    Performs tests with unpromoted unit as test subject.
    """

    def setUp(self):
        """
        Initializes unpromoted unit.
        """
        self.morph = Morph4("Lex")
        super().setUp()

    def test_get_promotion_item(self):
        """
        Demonstrates `get_promotion_item` for unpromoted unit.
        """
        lex = self.morph
        actual = lex.get_promotion_item()
        expected = "*Promote at Base*"
        self.assertEqual(actual, expected)

    def test_lex(self):
        """
        Simulates maxing.
        """
        lex = self.morph
        self.assertLess(lex.current_lv, 20)
        with self.assertRaises(PromotionError) as exc_ctx:
            lex.promote()
        actual = exc_ctx.exception.reason
        expected = PromotionError.Reason.LEVEL_TOO_LOW
        self.assertEqual(actual, expected)
        lex.level_up(16)
        lex.promote()
        lex.level_up(10)
        self.assertEqual(lex.current_lv, 30)
        with self.assertRaises(LevelUpError):
            lex.level_up(1)

class FE4Nonpromotables(Morph4TestCase):
    """
    For all FE4 units who cannot be promoted.
    """

    def test_inventory_size(self):
        """
        Asserts that inventory size is seven.
        """
        expected = 7
        promotables = self._get_promotables(can_promote=False)
        for name in promotables:
            morph = Morph4(name, father="Lex")
            actual = morph.inventory_size
            self.assertEqual(actual, expected)

    def test_get_promotion_item__nonpromotables(self):
        """
        For units who cannot be promoted.
        """
        nonpromotables = self._get_promotables(can_promote=False)
        for name in nonpromotables:
            morph = Morph4(name, father="Lex")
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)

    def test_get_promotion_list__nonpromotables(self):
        """
        For units who cannot be promoted.
        """
        nonpromotables = self._get_promotables(can_promote=False)
        expected = []
        for name in nonpromotables:
            morph = Morph4(name, father="Lex")
            actual = morph.get_promotion_list()
            self.assertListEqual(actual, expected)

    def test_nonkids_who_cannot_promote(self):
        """
        For nonchildren who cannot be promoted.
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

    def test_kids_who_cannot_promote(self):
        """
        For children who cannot be promoted.
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

class FE4Promotables(Morph4TestCase):
    """
    For all FE4 units who can be promoted.
    """

    def test_inventory_size(self):
        """
        Asserts that inventory size is seven.
        """
        expected = 7
        promotables = self._get_promotables(can_promote=True)
        for name in promotables:
            morph = Morph4(name, father="Lex")
            actual = morph.inventory_size
            self.assertEqual(actual, expected)

    def test_get_promotion_item__promotables(self):
        """
        For units who can be promoted.
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

    def test_get_promotion_list__promotables(self):
        """
        For units who can be promoted.
        """
        promotables = self._get_promotables(can_promote=True)
        for name in promotables:
            morph = Morph4(name, father="Lex")
            actual = morph.get_promotion_list()
            self.assertTrue(actual)

    def test_nonkids_who_can_promote(self):
        """
        For nonchildren who can be promoted.
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

    def test_kids_who_can_promote(self):
        """
        For children who can be promoted.
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

class FE4PromotedUnit(Morph4TestCase):
    """
    Performs tests with promoted unit as test subject.
    """

    def setUp(self):
        """
        Initializes promoted unit.
        """
        self.morph = Morph4("Sigurd")
        super().setUp()

    def test_get_promotion_item(self):
        """
        Demonstrates `get_promotion_item` for promoted unit.
        """
        sigurd = self.morph
        self.assertEqual(sigurd.max_level, 30)
        #with self.assertRaises(ValueError):
        actual = sigurd.get_promotion_item()
        self.assertIsNone(actual)

    def test_inventory_size(self):
        """
        Asserts that inventory size is seven.
        """
        sigurd = self.morph
        actual = sigurd.inventory_size
        self.assertIsInstance(actual, int)
        self.assertEqual(actual, 7)

    def test_sigurd(self):
        """
        Simulates maxing.
        """
        sigurd = self.morph
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

    def test_use_stat_booster(self):
        """
        Test inability to use stat booster.
        """
        sigurd = self.morph
        with self.assertRaises(StatBoosterError) as err_ctx:
            sigurd._use_stat_booster(None, None)
        actual = err_ctx.exception.reason
        expected = StatBoosterError.Reason.NO_IMPLEMENTATION
        self.assertEqual(actual, expected)

class FE4ChildUnit(Morph4TestCase):
    """
    Performs tests with child unit as test subject.
    """

    def setUp(self):
        """
        Initializes child unit.
        """
        self.morph = Morph4("Lakche", father="Lex")
        super().setUp()

    def test_level_up(self):
        """
        Simulates level up.
        """
        lakche = self.morph
        lakche.level_up(10)
        bases = {
            "HP": 30,
            "Str": 10,
            "Mag": 0,
            "Skl": 13,
            "Spd": 13,
            "Lck": 8,
            "Def": 7,
            "Res": 0,
        }
        growths = {
            "HP": 125,
            "Str": 50,
            "Mag": 7,
            "Skl": 70,
            "Spd": 40,
            "Lck": 30,
            "Def": 60,
            "Res": 7,
        }
        for stat in growths:
            expected = bases[stat] * 100 + growths[stat] * 10
            actual = getattr(lakche.current_stats, stat)
            self.assertEqual(actual, expected)

    def test_lakche_with_father_lex(self):
        """
        Simulates maxing.
        """
        lakche = self.morph
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

class Morph5TestCase(unittest.TestCase):
    """
    Provides framework for testing FE5 units.
    """

    def setUp(self):
        """
        Defines scroll list.
        """
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
        logger.critical("%s", self.id())

    @staticmethod
    def _get_promotables(can_promote):
        """
        Gets a list of units who can / cannot promote.
        """
        url_name = "thracia-776"
        return _get_promotables(url_name, can_promote=can_promote)

class FE5Promotables(Morph5TestCase):
    """
    Runs tests on all FE5 units who can promote.
    """

    def test_get_promotion_list__promotables(self):
        """
        Asserts that promotion list is non-empty.
        """
        promotables = self._get_promotables(can_promote=True)
        for name in filter(lambda name_: name_ != "Lara", promotables):
            morph = Morph5(name)
            actual = morph.get_promotion_list()
            self.assertTrue(actual)

    def test_get_promotion_item__promotables(self):
        """
        Validates output of method for units who can promote.
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

    @unittest.skip("Time-consuming.")
    def test_promotables(self):
        """
        Max out all units.
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

class FE5Unpromotables(Morph5TestCase):
    """
    Runs tests on all FE5 units who cannot promote.
    """

    def test_get_promotion_list__nonpromotables(self):
        """
        Asserts that promotion list is empty.
        """
        nonpromotables = self._get_promotables(can_promote=False)
        expected = []
        for name in nonpromotables:
            morph = Morph5(name)
            actual = morph.get_promotion_list()
            self.assertListEqual(actual, expected)

    def test_get_promotion_item__nonpromotables(self):
        """
        Validates output of method for units who cannot promote.
        """
        nonpromotables = self._get_promotables(can_promote=False)
        for name in nonpromotables:
            morph = Morph5(name)
            actual = morph.get_promotion_item()
            logger.debug("Promo-item for '%s' is: '%s'", name, actual)
            self.assertIsNone(actual)

    @unittest.skip("Time-consuming.")
    def test_nonpromotables(self):
        """
        Max out all units.
        """
        nonpromotables = self._get_promotables(can_promote=False)
        logger.debug("%s", nonpromotables)
        for name in nonpromotables:
            morph = Morph5(name)
            morph.level_up(20 - morph.current_lv)
            with self.assertRaises(LevelUpError):
                morph.level_up(1)

class FE5Leif(Morph5TestCase):
    """
    Tests centered around FE5!Leif.
    """

    def setUp(self):
        """
        Initializes Morph for Leif.
        """
        self.morph = Morph5("Leaf")
        super().setUp()

    def test_use_stat_booster__maxed_stat(self):
        """
        Trying to use a stat booster when the stat it boosts is maxed.
        """
        leaf = self.morph
        leaf.current_stats.Spd = 2000
        with self.assertRaises(StatBoosterError) as exception_ctx:
            leaf.use_stat_booster("Speed Ring")
        exception = exception_ctx.exception
        actual = exception.reason
        expected = StatBoosterError.Reason.STAT_IS_MAXED
        self.assertEqual(actual, expected)
        actual = exception.max_stat
        expected = ("Spd", 2000)
        self.assertTupleEqual(actual, expected)

    def test_inventory_size(self):
        """
        Assert inventory size is seven.
        """
        leaf = self.morph
        actual = leaf.inventory_size
        expected = 7
        self.assertEqual(actual, expected)

    def test_get_promotion_item(self):
        """
        Inspects method output for Morph with exceptional promotion conditions.
        """
        leif = self.morph
        actual = leif.get_promotion_item()
        expected = "*Chapter 18 - End*"
        self.assertEqual(actual, expected)
        leif.promote()
        actual = leif.get_promotion_item()
        self.assertIsNone(actual)

    def test_inventory_size(self):
        """
        Inventory size is seven.
        """
        leif = self.morph
        actual = leif.inventory_size
        self.assertIsInstance(actual, int)
        self.assertEqual(actual, 7)

    def test_promote(self):
        """
        Leif can promote at level one.
        """
        name = "Leaf"
        morph = Morph5(name)
        self.assertLess(morph.current_lv, 10)
        morph.promote()
        self.assertEqual(morph.current_clstype, "classes__promotion_gains")
        with self.assertRaises(PromotionError):
            morph.promote()

    def test_get_promotion_item__has_been_promoted(self):
        """
        Asserts that promotion item post-promotion is None.
        """
        leif = self.morph
        leif.promote()
        #with self.assertRaises(ValueError):
        actual = leif.get_promotion_item()
        self.assertIsNone(actual)

class FE5Linoan(Morph5TestCase):
    """
    Tests centered around FE5!Linoan.
    """

    def setUp(self):
        """
        Initializes Morph for Linoan.
        """
        self.morph = Morph5("Linoan")
        super().setUp()

    def test_get_promotion_item(self):
        """
        Inspects method output for Morph with exceptional promotion conditions.
        """
        name = "Linoan"
        linoan = Morph5(name)
        actual = linoan.get_promotion_item()
        expected = "*Chapter 21 - Church*"
        self.assertEqual(actual, expected)
        linoan.promote()
        actual = linoan.get_promotion_item()
        self.assertIsNone(actual)

    def test_promote(self):
        """
        Linoan can promote at level one.
        """
        name = "Linoan"
        morph = Morph5(name)
        self.assertLess(morph.current_lv, 10)
        morph.promote()
        self.assertEqual(morph.current_clstype, "classes__promotion_gains")
        with self.assertRaises(PromotionError):
            morph.promote()

class FE5Lara(Morph5TestCase):
    """
    Tests centered around FE5!Linoan.
    """

    def setUp(self):
        """
        Initializes Morph for Linoan.
        """
        self.morph = Morph5("Lara")
        super().setUp()

    def test_long_path(self):
        """
        Max out on the long path: Thief -> Thief Fighter -> Dancer -> Thief Fighter
        """
        lara = self.morph
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

    def test_short_path(self):
        """
        Max out on the short path: Thief -> Dancer -> Thief Fighter
        """
        lara = self.morph
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

    def test_get_promotion_item(self):
        """
        Inspects method output for the longer of Lara's promotion paths.
        """
        lara = self.morph
        lara.promo_cls = "Dancer"
        actual = lara.get_promotion_item()
        expected = "*Chapter 12x - Talk to Perne*"
        self.assertEqual(actual, expected)
        lara.promote() # to: Dancer
        actual = lara.get_promotion_item()
        expected = "Knight Proof"
        self.assertEqual(actual, expected)
        lara.level_up(10 - lara.current_lv)
        lara.promote() # to: Thief Fighter
        actual = lara.get_promotion_item()
        self.assertIsNone(actual)

    def test_get_promotion_item__no_dancer(self):
        """
        Inspects method output for the shorter of Lara's promotion paths.
        """
        lara = self.morph
        lara.level_up(10 - lara.current_lv)
        lara.promo_cls = "Thief Fighter"
        actual = lara.get_promotion_item()
        expected = "Knight Proof"
        self.assertEqual(actual, expected)
        lara.promote() # to Thief Fighter
        actual = lara.get_promotion_item()
        expected = "*Chapter 12x - Talk to Perne*"
        self.assertEqual(actual, expected)
        lara.promote() # to Dancer
        lara.level_up(10 - lara.current_lv)
        actual = lara.get_promotion_item()
        expected = "Knight Proof"
        lara.promote() # to Thief Fighter
        actual = lara.get_promotion_item()
        self.assertIsNone(actual)

    def test_get_promotion_item__is_maxed_out(self):
        """
        Inspects output for a Lara who cannot promote futher.
        """
        lara = self.morph
        lara.promo_cls = "Dancer"
        lara.promote()
        lara.level_up(10 - lara.current_lv)
        lara.promote()
        actual = lara.get_promotion_item()
        self.assertIsNone(actual)


class FE5PromotedUnit(Morph5TestCase):
    """
    Tests centered around a unit who cannot be promoted in FE5.
    """

    def test_get_promotion_item__promoted(self):
        morph = Morph5("Evayle")
        actual = morph.get_promotion_item()
        self.assertIsNone(actual)

class FE5Eda(Morph5TestCase):
    """
    Tests centered around FE5!Eda.
    """

    def setUp(self):
        """
        Initializes Morph for Linoan.
        """
        self.morph = Morph5("Eda")
        super().setUp()

    def test_apply_scroll_bonuses__negatives_are_zeroed_out(self):
        """
        Asserts that effectively negative growth rates are zero.
        """
        eda = self.morph
        eda.equipped_scrolls[None] = eda.Stats(**eda.Stats.get_stat_dict(-200))
        eda._apply_scroll_bonuses()
        actual = all(eda.growth_rates == eda.Stats(**eda.Stats.get_stat_dict(0)))
        expected = True
        self.assertIs(actual, expected)

    def test_unequip_scroll(self):
        """
        Tests equipping and unequipping of scrolls.
        """
        eda = self.morph
        scrolls_to_equip = (
            "Blaggi",
            "Heim",
            "Fala",
        )
        for scroll in scrolls_to_equip:
            eda.equip_scroll(scroll)
        eda.unequip_scroll(scroll)
        actual = set(eda.equipped_scrolls)
        expected = set(scrolls_to_equip) - {"Fala"}
        self.assertSetEqual(actual, expected)

    def test_unequip_scroll2(self):
        """
        Trying to unequip a scroll that DNE.
        """
        eda = self.morph
        with self.assertRaises(ScrollError) as err_ctx:
            eda.unequip_scroll("")
        err = err_ctx.exception
        actual = err.reason
        expected = ScrollError.Reason.NOT_EQUIPPED
        self.assertEqual(actual, expected)
        actual = err.absent_scroll
        expected = ""
        self.assertEqual(actual, expected)

    def test_equip_scroll(self):
        """
        Trying to equip a scroll that is already equipped.
        """
        eda = self.morph
        scroll_to_equip = "Heim"
        eda.equip_scroll(scroll_to_equip)
        with self.assertRaises(ScrollError) as err_ctx:
            eda.equip_scroll(scroll_to_equip)
        err = err_ctx.exception
        actual = err.reason
        expected = ScrollError.Reason.ALREADY_EQUIPPED
        self.assertEqual(actual, expected)
        actual = err.equipped_scroll
        expected = scroll_to_equip
        self.assertEqual(actual, expected)

    def test_equip_scroll2(self):
        """
        Trying to equip a scroll that is already equipped.
        """
        eda = self.morph
        scroll_name = self.scrolls[0]
        og_growths = eda.growth_rates.copy()
        eda.equip_scroll(scroll_name)
        self.assertIn(scroll_name, eda.equipped_scrolls)
        self.assertEqual(len(eda.equipped_scrolls), 1)
        new_growths = eda.growth_rates
        actual = all(og_growths == new_growths)
        expected = False
        self.assertIs(actual, expected)
        with self.assertRaises(ScrollError) as err_ctx:
            eda.equip_scroll(scroll_name)
        actual = err_ctx.exception.reason
        expected = ScrollError.Reason.ALREADY_EQUIPPED
        self.assertEqual(actual, expected)

    def test_equip_scroll__invalid_scroll(self):
        """
        Trying to equip a scroll that DNE.
        """
        eda = self.morph
        with self.assertRaises(ScrollError) as err_ctx:
            eda.equip_scroll("")
        err = err_ctx.exception
        actual = err.reason
        expected = ScrollError.Reason.NOT_FOUND
        self.assertEqual(actual, expected)
        actual = err.valid_scrolls
        logger.debug("valid_scrolls: %s", actual)
        expected = [
            'Baldo',
            'Blaggi',
            'Dain',
            'Fala',
            'Heim',
            'Hezul',
            'Neir',
            'Noba',
            'Odo',
            'Sety',
            'Tordo',
            'Ulir',
        ]
        self.assertListEqual(actual, expected)

    def test_equip_scroll__invalid_scroll2(self):
        """
        Trying to equip a scroll that DNE.
        """
        scroll_name = ""
        eda = self.morph
        og_growths = eda.growth_rates.copy()
        with self.assertRaises(ScrollError) as err_ctx:
            eda.equip_scroll(scroll_name)
        # check error
        actual = err_ctx.exception.reason
        expected = ScrollError.Reason.NOT_FOUND
        self.assertEqual(actual, expected)
        # check state
        self.assertNotIn(scroll_name, eda.equipped_scrolls)
        self.assertEqual(len(eda.equipped_scrolls), 0)
        new_growths = eda.growth_rates
        actual = all(og_growths == new_growths)
        expected = True
        self.assertIs(actual, expected)

    def test_equip_scroll__exceed_inventory_space(self):
        """
        Equipping a scroll with an inventory that is full.
        """
        # equip scrolls
        eda = self.morph
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

    def test_level_up__hezul_scroll(self):
        """
        Test output of levelling up with a scroll equipped.
        """
        eda = self.morph
        eda.equip_scroll("Hezul")
        # HP +30, Str +10, Lck -10
        #expected = [(stat, value) for stat, value in eda.current_stats.as_list()]
        eda.level_up(10)
        eda2 = Morph5("Eda")
        eda2.equip_scroll("Hezul")
        eda2.unequip_scroll("Hezul")
        eda2.level_up(10)
        diff = {
            "HP": 300,
            "Str": 100,
            "Lck": -100,
        }
        for stat, expected in diff.items():
            actual = getattr(eda.current_stats, stat) - getattr(eda2.current_stats, stat)
            self.assertEqual(actual, expected)

class Morph6TestCase(unittest.TestCase):
    """
    Provides framework for testing FE6 units.
    """

    def setUp(self):
        """
        Logs test-id to demarcate test in log report.
        """
        logger.critical("%s", self.id())

    @staticmethod
    def _get_promotables(can_promote):
        """
        Gets list of units filtered by whether or not they can promote.
        """
        url_name = "binding-blade"
        return _get_promotables(url_name, can_promote)

class Morph6Class(Morph6TestCase):
    """
    Conducts tests on the Morph6 class itself.
    """

    def test_get_true_character_list6(self):
        """
        Validates character list.
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
            #'Narshen',
            #'Gale',
            #'Hector',
            #'Brunya',
            #'Eliwood',
            #'Murdoch',
            #'Zephiel',
            #'Guinevere',
        )
        actual = tuple(Morph6.get_true_character_list())
        self.assertTupleEqual(actual, expected)


class FE6Gonzales(Morph6TestCase):
    """
    Conduct series of tests with FE6!Gonzales as subject.
    """

    def test_gonzales__no_route_or_hm(self):
        """
        What happens when one tries to initialize a Morph with neither route nor mode.
        """
        with self.assertRaises(InitError) as err_ctx:
            Morph6("Gonzales", hard_mode=None, route=None)
        err = err_ctx.exception
        actual = err.missing_value
        expected = InitError.MissingValue.HARD_MODE_AND_ROUTE
        self.assertEqual(actual, expected)
        actual = err.init_params
        expected = {"route": ("Lalum", "Elphin")}
        self.assertDictEqual(actual, expected)
        actual = err.init_params2
        expected = {"hard_mode": (False, True)}
        self.assertDictEqual(actual, expected)

    def test_gonzales__lalum_route(self):
        """
        Get Morph of Gonzales on Lalum's route.
        """
        morph = Morph6("Gonzales", hard_mode=True, route="Lalum")
        actual = morph.current_lv
        expected = 5
        self.assertEqual(actual, expected)

    def test_gonzales__elphin_route(self):
        """
        Get Morph of Gonzales on Lalum's route.
        """
        morph = Morph6("Gonzales", hard_mode=True, route="Elphin")
        actual = morph.current_lv
        expected = 11
        self.assertEqual(actual, expected)

    def test_gonzales__no_route(self):
        """
        Get Morph of Gonzales without a specified route.
        """
        with self.assertRaises(InitError) as err_ctx:
            Morph6("Gonzales", hard_mode=True, route=None)
        err = err_ctx.exception
        actual = err.missing_value
        expected = InitError.MissingValue.ROUTE
        self.assertEqual(actual, expected)
        actual = err.init_params
        expected = {"route": ("Lalum", "Elphin")}
        self.assertDictEqual(actual, expected)
        actual = err.init_params2
        self.assertIsNone(actual)

    def test_gonzales__no_hm(self):
        """
        Get Morph of Gonzales without a specified mode.
        """
        with self.assertRaises(InitError) as err_ctx:
            Morph6("Gonzales", hard_mode=None, route="Lalum")
        err = err_ctx.exception
        actual = err.missing_value
        expected = InitError.MissingValue.HARD_MODE
        self.assertEqual(actual, expected)
        actual = err.init_params
        expected = {"hard_mode": (False, True)}
        self.assertDictEqual(actual, expected)
        actual = err.init_params2
        self.assertIsNone(actual)


class FE6Unpromotables(Morph6TestCase):
    """
    Conduct series of tests with unpromotable units of FE6 as subjects.
    """

    def test_get_promotion_list(self):
        """
        Asserts that promotion lists for these lot are empty.
        """
        nonpromotables = self._get_promotables(can_promote=False)
        expected = []
        for name in nonpromotables:
            if name == "Narshen":
                break
            morph = Morph6(name, hard_mode=True)
            actual = morph.get_promotion_list()
            self.assertListEqual(actual, expected)

    def test_get_promotion_item__nonpromotables(self):
        """
        Asserts that promotion lists for these lot are null.
        """
        nonpromotables = self._get_promotables(can_promote=False)
        #expected = None
        for name in filter(lambda name_: " (HM)" not in name_, nonpromotables):
            if name == "Narshen":
                break
            try:
                morph = Morph6(name)
            except InitError:
                morph = Morph6(name, hard_mode=True)
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)

    def test_nonpromotables(self):
        """
        Simulates maxing.
        """
        nonpromotables = self._get_promotables(False)
        for name in nonpromotables:
            if name == "Narshen":
                break
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

class FE6Promotables(Morph6TestCase):
    """
    Conduct series of tests with promotable units of FE6 as subjects.
    """

    def test_get_promotion_list(self):
        """
        Asserts promotion lists are non-empty.
        """
        promotables = self._get_promotables(can_promote=True)
        #expected = []
        for name in promotables:
            morph = Morph6(name, hard_mode=True, number_of_declines=0, route="Lalum")
            actual = morph.get_promotion_list()
            self.assertTrue(actual)

    def test_get_promotion_item(self):
        """
        Checks that the promotion item for each promotable is as expected.
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
                kwargs = {}
                if name == "Hugh":
                    kwargs['number_of_declines'] = 3
                elif name == "Gonzales":
                    kwargs['route'] = "Lalum"
                morph = Morph6(name, hard_mode=True, **kwargs)
            actual = morph.get_promotion_item()
            expected = promoitem_dict.pop(name)
            self.assertEqual(actual, expected)
            # extra
            morph.level_up(20 - morph.current_lv)
            morph.promote()
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)

    def test_promotables(self):
        """
        Maxing.
        """
        promotables = self._get_promotables(True)
        for name in promotables:
            hard_mode = " (HM)" in name
            name = name.replace(" (HM)", "")
            logger.debug("Morph6(%r, hard_mode=%r)", name, hard_mode)
            kwargs = {}
            if name == "Hugh":
                kwargs['number_of_declines'] = 3
            elif name == "Gonzales":
                kwargs['route'] = "Lalum"
            morph = Morph6(name, hard_mode=hard_mode, **kwargs)
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

class FE6Rutger(Morph6TestCase):
    """
    Conduct series of tests with FE6!Rutger as subject.
    """

    def test_hardmode_explicit_and_via_option(self):
        """
        Checks the initialization of Rutger Morph.
        """
        hm_morph1 = Morph6("Rutger (HM)")
        hm_morph2 = Morph6("Rutger", hard_mode=True)
        expected = True
        actual = all((hm_morph1.current_stats == hm_morph2.current_stats).as_dict().values())
        self.assertIs(actual, expected)

    def test_no_hardmode_specified(self):
        """
        Try to initialize Rutger Morph without specifying hard_mode option.
        """
        with self.assertRaises(InitError) as exc_ctx:
            rutger = Morph6("Rutger")
        exception = exc_ctx.exception
        actual = exception.missing_value
        expected = InitError.MissingValue.HARD_MODE
        self.assertEqual(actual, expected)
        actual = exception.init_params
        expected = {"hard_mode": (False, True)}
        self.assertDictEqual(actual, expected)

    def test_hardmode_version_exists(self):
        """
        Validate _meta['Hard Mode'] value.
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
        Validate stat differences across difficulty modes.
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

class FE6Roy(Morph6TestCase):
    """
    Conduct series of tests with FE6!Roy as subject.
    """

    def setUp(self):
        """
        Initialize Morph instance for Roy
        """
        self.morph = Morph6("Roy")
        super().setUp()

    def test_no_hardmode_version(self):
        """
        Demo of initializing a non-HM unit with `hard_mode` specified.
        """
        with self.assertLogs(logger, logging.WARNING):
            wolt = Morph6("Roy", hard_mode=True)
        self.assertIsNone(wolt._meta["Hard Mode"])

    def test_inventory_size(self):
        """
        Assert inventory size is equal to 0.
        """
        roy = self.morph
        actual = roy.inventory_size
        self.assertIsInstance(actual, int)
        self.assertEqual(actual, 0)

    def test_inventory_size2(self):
        """
        Assert inventory size is equal to 0.
        """
        lord = Morph6("Roy")
        actual = lord.inventory_size
        expected = 0
        self.assertEqual(actual, expected)

    def test_promote__early(self):
        """
        Assert that Roy can promote at level one.
        """
        roy = self.morph
        self.assertEqual(roy.current_lv, 1)
        roy.promote()
        self.assertEqual(roy.current_clstype, "classes__promotion_gains")

    def test_promote__early2(self):
        """
        Assert that Roy can promote at level one.
        """
        morph = Morph6("Roy")
        #self.assertEqual(roy.current_lv, 1)
        self.assertLess(morph.current_lv, 10)
        morph.promote()
        self.assertEqual(morph.current_cls, "Master Lord")
        with self.assertRaises(PromotionError):
            morph.promote()

    def test_stat_boosters(self):
        """
        Use a bunch of stat boosters.
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
            expected = getattr(original_stats, stat) + bonus * 100
            actual = getattr(morph.current_stats, stat)
            self.assertEqual(actual, expected)

class FE6Hugh(Morph6TestCase):
    """
    Conduct series of tests with FE6!Hugh as subject.
    """

    def setUp(self):
        """
        Initialize Morph instance for FE6!Hugh.
        """
        self.morph = self._create_control_hugh()
        super().setUp()

    @staticmethod
    def _create_control_hugh():
        """
        Creates a Morph of Hugh with no alterations.
        """
        control_morph = Morph6("Roy")
        control_morph._name = "Hugh"
        stat_dict = {
            "HP": 26,
            "Pow": 13,
            "Skl": 11,
            "Spd": 12,
            "Lck": 10,
            "Def": 9,
            "Res": 9,
            "Con": 7,
            "Mov": 5,
        }
        control_morph.current_stats = control_morph.Stats(**stat_dict)
        return control_morph

    def test_as_string(self):
        """
        Prints repr to log.
        """
        hugh = self.morph
        actual = hugh.as_string()
        self.assertIsInstance(actual, str)
        logger.debug("as_string -> %s", actual)

    def test_hugh__INVALID_number_of_declines(self):
        """
        Try initializing Morph of Hugh with invalid decline count.
        """
        number_of_declines = "fish"
        with self.assertRaises(InitError) as err_ctx:
            Morph6("Hugh", number_of_declines=number_of_declines)
        error = err_ctx.exception
        actual = error.missing_value
        expected = InitError.MissingValue.NUMBER_OF_DECLINES
        self.assertEqual(actual, expected)
        actual = error.init_params
        expected = {"number_of_declines": (0, 1, 2, 3)}
        self.assertDictEqual(actual, expected)

    def test_hugh__number_of_declines0(self):
        """
        Validate own helper function. (TODO: Consider deleting.)
        """
        number_of_declines = 0
        morph = Morph6("Hugh", number_of_declines=number_of_declines)
        control_morph = self._create_control_hugh()
        actual = all(morph.current_stats == control_morph.current_stats)
        expected = True
        self.assertIs(actual, expected)

    def test_hugh__number_of_declines__nonzero(self):
        """
        Validates stats of Hugh across decline-counts.
        """
        for number_of_declines in range(1, 4):
            morph = Morph6("Hugh", number_of_declines=number_of_declines)
            Stats = morph.STATS()
            # create control case
            stat_dict = Stats.get_stat_dict(-number_of_declines)
            stat_dict["Con"] = 0
            stat_dict["Mov"] = 0
            decrement = Stats(**stat_dict)
            control_morph = self._create_control_hugh()
            control_morph.current_stats += decrement
            # compare
            actual = all(morph.current_stats == control_morph.current_stats)
            expected = True
            self.assertIs(actual, expected)

    def test_not_hugh__number_of_declines3(self):
        """
        Checks that logger warns user if `num_declines` is specified for non-Hugh units.
        """
        number_of_declines = 3
        with self.assertLogs(logger, logging.WARNING):
            morph = Morph6("Roy", number_of_declines=number_of_declines)
        actual = morph._meta["Number of Declines"]
        self.assertIsNone(actual)

class Morph7TestCase(unittest.TestCase):
    """
    Provides framework for testing FE7 units.
    """

    def setUp(self):
        """
        Logs test-id to demarcate test in log.
        """
        self.lyndis_league = (
            "Lyn",
            "Sain",
            "Kent",
            "Florina",
            "Wil",
            "Dorcas",
            "Erk",
            "Serra",
            "Matthew",
            "Rath",
            "Nils",
            "Lucius",
            "Wallace",
        )
        logger.critical("%s", self.id())

    @staticmethod
    def _get_promotables(can_promote):
        """
        Get list of units filtered by ability to promote.
        """
        # query for list of units who cannot promote
        url_name = "blazing-sword"
        return _get_promotables(url_name, can_promote=can_promote)

class Morph7Class(Morph7TestCase):
    """
    Conduct series of tests on Morph7 class itself.
    """

    def test_get_true_character_list7(self):
        """
        Validates `get_true_character_list`.
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

class FE7Ninian(Morph7TestCase):
    """
    Conduct series of tests with FE7!Ninian as subject.
    """

    def test_ninian__lyn_mode(self):
        """
        Attempting to initialize LM!Ninian results in an error.
        """
        with self.assertRaises(UnitNotFoundError):
            Morph7("Ninian", lyn_mode=True)

class FE7Hector(Morph7TestCase):
    """
    Conduct series of tests with FE7!Hector as subject.
    """

    def setUp(self):
        """
        Initializes morph instances.
        """
        self.morph = Morph7("Hector")
        super().setUp()

    def test_promote__early(self):
        """
        Emphasize special promotion.
        """
        hector = self.morph
        self.assertLess(hector.current_lv, 10)
        hector.promote()
        self.assertEqual(hector.current_clstype, "classes__promotion_gains")
        with self.assertRaises(PromotionError):
            hector.promote()

class FE7Eliwood(Morph7TestCase):
    """
    Conduct series of tests with FE7!Eliwood as subject.
    """

    def setUp(self):
        """
        Initializes morph instances.
        """
        self.morph = Morph7("Eliwood")
        super().setUp()

    def test_eliwood(self):
        """
        Maxing.
        """
        eliwood = self.morph
        actual = eliwood.current_lv
        expected = 1
        self.assertEqual(actual, expected)
        bases = {
            "HP": 1800,
            "Pow": 500,
            "Skl": 500,
            "Spd": 700,
            "Lck": 700,
            "Def": 500,
            "Res": 0,
            "Con": 700,
            "Mov": 500,
        }
        for stat, expected in bases.items():
            actual = getattr(eliwood.current_stats, stat)
            self.assertEqual(actual, expected)
        eliwood.level_up(19)
        stats_at_lv20 = {
            "HP": 3320,
            "Pow": 1355,
            "Skl": 1450,
            "Spd": 1460,
            "Lck": 1555,
            "Def": 1070,
            "Res": 665,
            "Con": 700,
            "Mov": 500,
        }
        for stat, expected in stats_at_lv20.items():
            actual = getattr(eliwood.current_stats, stat)
            self.assertEqual(actual, expected)
        eliwood.promote()
        stats_at_lv20_01 = {
            "HP": 3720,
            "Pow": 1555,
            "Skl": 1450,
            "Spd": 1560,
            "Lck": 1555,
            "Def": 1170,
            "Res": 965,
            "Con": 900,
            "Mov": 700,
        }
        for stat, expected in stats_at_lv20_01.items():
            actual = getattr(eliwood.current_stats, stat)
            self.assertEqual(actual, expected)
        eliwood.use_stat_booster("Angelic Robe")
        expected = 4420
        actual = eliwood.current_stats.HP
        self.assertEqual(actual, expected)

    def test_inventory_size(self):
        """
        Validate inventory size.
        """
        eliwood = self.morph
        actual = eliwood.inventory_size
        self.assertIsInstance(actual, int)
        self.assertEqual(actual, 0)

    def test_promote__early(self):
        """
        Emphasize special promotion.
        """
        eliwood = self.morph
        self.assertLess(eliwood.current_lv, 10)
        #self.assertEqual(morph.current_lv, 1)
        eliwood.promote()
        self.assertEqual(eliwood.current_clstype, "classes__promotion_gains")
        with self.assertRaises(PromotionError):
            eliwood.promote()

    def test_stat_boosters(self):
        """
        Demo stat booster usage.
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
        eliwood = self.morph
        for item, statbonus in item_bonus_dict.items():
            original_stats = eliwood.current_stats.copy()
            eliwood.use_stat_booster(item)
            stat, bonus = statbonus
            expected = getattr(original_stats, stat) + bonus * 100
            actual = getattr(eliwood.current_stats, stat)
            self.assertEqual(actual, expected)

    def test_inventory_size(self):
        """
        Validate inventory size.
        """
        lord = Morph7("Eliwood")
        actual = lord.inventory_size
        expected = 0
        self.assertEqual(actual, expected)

class FE7Nino(Morph7TestCase):
    """
    Conduct series of tests with FE7!Nino as subject.
    """

    def setUp(self):
        """
        Initializes morph instances.
        """
        self.morph = Morph7("Nino")
        super().setUp()


    def test_level_up(self):
        """
        Tests level-up function.
        """
        nino = self.morph
        nino.use_afas_drops()
        nino.level_up(10)
        stats_at_lv15 = {
            "HP": 2450,
            "Pow": 1200,
            "Skl": 1350,
            "Spd": 1700,
            "Lck": 1450,
            "Def": 550,
            "Res": 1200,
        }
        for stat, expected in stats_at_lv15.items():
            actual = getattr(nino.current_stats, stat)
            expected += 5 * 10
            self.assertEqual(actual, expected)

    def test_afas_drops(self):
        """
        Tests use of Afa's Drops.
        """
        nino = self.morph
        nino.use_afas_drops()
        nino2 = Morph7("Nino")
        diff = (nino.growth_rates - nino2.growth_rates).as_dict()
        self.assertSetEqual(set(diff.values()), {5, None})
        with self.assertRaises(GrowthsItemError) as err_ctx:
            nino.use_afas_drops()
        actual = err_ctx.exception.reason
        expected = GrowthsItemError.Reason.ALREADY_CONSUMED
        self.assertEqual(actual, expected)

class FE7Unpromotables(Morph7TestCase):
    """
    Conduct series of tests with FE7 unpromotable units as subjects.
    """

    def test_get_promotion_list(self):
        """
        Asserts that promo-list is empty.
        """
        nonpromotables = self._get_promotables(can_promote=False)
        expected = []
        for name in nonpromotables:
            morph = Morph7(name, lyn_mode=False, hard_mode=True)
            actual = morph.get_promotion_list()
            self.assertListEqual(actual, expected)

    def test_get_promotion_item(self):
        """
        Asserts that promo-item is null.
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

    def test_nonpromotables(self):
        """
        Maxing.
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

class FE7Promotables(Morph7TestCase):
    """
    Conduct series of tests with FE7 promotable units as subjects.
    """

    def test_get_promotion_list(self):
        """
        Assert that list is non-empty.
        """
        promotables = self._get_promotables(can_promote=True)
        #expected = []
        for name in promotables:
            morph = Morph7(name, lyn_mode=True, hard_mode=True)
            actual = morph.get_promotion_list()
            self.assertTrue(actual)

    def test_promotables(self):
        """
        Maxing.
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

    def test_get_promotion_item(self):
        """
        Check that each character is assigned the right promo-item.
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

class FE7HardModeUnit(Morph7TestCase):
    """
    Conduct series of tests with FE7 HM-unit as subject.
    """

    def setUp(self):
        """
        Initializes Morph for Raven.
        """
        #self.morph = Morph7("Raven")
        super().setUp()

    def test_raven_no_hardmode_specified(self):
        """
        Try initializing HM-unit without hard-mode option.
        """
        with self.assertRaises(InitError) as exc_ctx:
            raven = Morph7("Raven")
        exception = exc_ctx.exception
        actual = exception.missing_value
        expected = InitError.MissingValue.HARD_MODE
        self.assertEqual(actual, expected)
        actual = exception.init_params
        expected = {"hard_mode": (False, True)}
        self.assertDictEqual(actual, expected)

    def test_copy(self):
        """
        Test copy method of Morph.
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

    def test_hardmode_override(self):
        """
        What happens when you try to manually query HM version of character
        """
        raven = Morph7("Raven (HM)", hard_mode=False)
        self.assertIsNone(raven._meta["Hard Mode"])
        raven2 = Morph7("Raven", hard_mode=True)
        self.assertIs(raven2._meta["Hard Mode"], True)
        diff = (raven.current_stats - raven2.current_stats).as_dict()
        self.assertSetEqual(set(diff.values()), {0, None})

    def test_hardmode_version_exists(self):
        """
        Validates `_meta['Hard Mode']` parameter of morph instance.
        """
        hard_mode = False
        raven = Morph7("Raven", hard_mode=hard_mode)
        self.assertIs(raven._meta["Hard Mode"], hard_mode)
        hard_mode = True
        raven2 = Morph7("Raven", hard_mode=hard_mode)
        self.assertIs(raven2._meta["Hard Mode"], hard_mode)
        self.assertEqual(raven2.name, "Raven")

    def test_hardmode_diff(self):
        """
        Confirms that non-HM and HM stats differ.
        """
        raven = Morph7("Raven", hard_mode=False)
        raven_hm = Morph7("Raven", hard_mode=True)
        diff = (raven.current_stats - raven_hm.current_stats).as_dict()
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

class FE7NormalOnlyUnit(Morph7TestCase):
    """
    Conduct series of tests with FE7 non-HM unit as subject.
    """

    def test_no_hardmode_version(self):
        """
        Asserts that logger prints warning for units without non-HM stats.
        """
        with self.assertLogs(logger, logging.WARNING):
            lyn = Morph7("Lyn", hard_mode=True, lyn_mode=True)
        self.assertIsNone(lyn._meta["Hard Mode"])

class FE7NonLyndisLeague(Morph7TestCase):
    """
    Conduct series of tests with unit not in FE7!'Lyndis League' as subject.
    """

    def test_not_in_lyndis_league(self):
        """
        Asserts that logger prints warning upon trying to specify a value for `lyn_mode`.
        """
        with self.assertLogs(logger, logging.WARNING):
            athos = Morph7("Athos", lyn_mode=True)
        self.assertIsNone(athos._meta["Lyn Mode"])

class FE7LyndisLeague(Morph7TestCase):
    """
    Conduct series of tests with FE7!'Lyndis League' unit as subject.
    """

    def test_no_lynmode_specified(self):
        """
        No value specified for `lyn_mode`.
        """
        with self.assertRaises(InitError) as exc_ctx:
            Morph7("Lyn")
        exception = exc_ctx.exception
        actual = exception.missing_value
        expected = InitError.MissingValue.LYN_MODE
        self.assertEqual(actual, expected)
        actual = exception.init_params
        expected = {"lyn_mode": (False, True)}
        self.assertDictEqual(actual, expected)

    def test_lyn(self):
        """
        Comparing across campaigns.
        """
        lyn = Morph7("Lyn", lyn_mode=True)
        self.assertIs(lyn._meta["Lyn Mode"], True)
        lyn2 = Morph7("Lyn", lyn_mode=False)
        self.assertIs(lyn2._meta["Lyn Mode"], False)
        diff = (lyn.current_stats - lyn2.current_stats).as_dict()
        self.assertNotEqual(set(diff.values()), {0})

    def test_lyndis_league(self):
        """
        Initialize all Lyn Mode units sans Wallace.
        """
        lyndis_league = (
            "Lyn",
            "Sain",
            "Kent",
            "Florina",
            "Wil",
            "Dorcas",
            "Erk",
            "Serra",
            "Matthew",
            "Rath",
            "Nils",
            "Lucius",
            #"Wallace",
        )
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

class FE7Wallace(Morph7TestCase):
    """
    Conduct series of tests with FE7!'Lyndis League' unit as subject.
    """

    def test_wallace__unpromoted(self):
        """
        Maxing LynMode version.
        """
        wallace = Morph7("Wallace", lyn_mode=True)
        wallace.level_up(20 - wallace.current_lv)
        wallace.promote()
        wallace.level_up(19)

    def test_wallace__promoted(self):
        """
        Maxing Bern version.
        """
        wallace = Morph7("Wallace", lyn_mode=False)
        wallace.level_up(20 - wallace.current_lv)
        with self.assertRaises(PromotionError) as err_ctx:
            wallace.promote()
        expected = err_ctx.exception.reason
        actual = PromotionError.Reason.NO_PROMOTIONS
        self.assertEqual(actual, expected)
        #wallace.level_up(19)

class Morph8TestCase(unittest.TestCase):
    """
    Provides framework for testing FE8 units.
    """

    def setUp(self):
        """
        Initializes trainee list.
        """
        self.trainees = ("Ross", "Amelia", "Ewan")
        logger.critical("%s", self.id())

    @staticmethod
    def _get_promotables(can_promote):
        """
        Get list of units filtered by ability to promote.
        """
        url_name = "the-sacred-stones"
        return _get_promotables(url_name, can_promote=can_promote)

    def _test_get_promotion_list__trainee(self, name):
        """
        Maxing framework.
        """
        _morph = Morph8(name)
        _morph.current_lv = 10
        _morph.promo_cls = None
        # compile list of promotions: tier 1
        try:
            _morph.promote()
        except PromotionError:
            possible_promotions = _morph.possible_promotions
        promo_dict = {}
        # compile list of promotions: tier 2
        for promo_cls in possible_promotions:
            morph = Morph8(name)
            morph.current_lv = 10
            morph.promo_cls = promo_cls
            morph.promote()
            morph.current_lv = 10
            try:
                morph.promote()
            except PromotionError:
                promo_dict[promo_cls] = morph.possible_promotions
        # the actual test
        for promo_cls, promoclasses2 in promo_dict.items():
            for promo_cls2 in promoclasses2:
                morph = Morph8(name)
                # test
                actual = morph.get_promotion_list()
                self.assertTrue(actual)
                # promote 1
                morph.current_lv = 10
                morph.promo_cls = promo_cls
                morph.promote()
                # test
                actual = morph.get_promotion_list()
                self.assertTrue(actual)
                # promote 2
                morph.current_lv = 10
                morph.promo_cls = promo_cls2
                morph.promote()
                # test
                actual = morph.get_promotion_list()
                expected = []
                self.assertListEqual(actual, expected)

    def _test_get_promotion_item__trainee(self, name, promotion_item):
        """
        Maxing framework.
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

    def _test_scrub(self, name):
        """
        Maxing framework.
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

class FE8Unpromotables(Morph8TestCase):
    """
    Conduct series of tests with FE8 unpromotable units as subjects.
    """

    def test_get_promotion_list(self):
        """
        Assert that promo-list is empty.
        """
        nonpromotables = self._get_promotables(can_promote=False)
        expected = []
        for name in nonpromotables:
            morph = Morph8(name)
            actual = morph.get_promotion_list()
            self.assertListEqual(actual, expected)

    def test_get_promotion_item(self):
        """
        Assert that promo-item is null.
        """
        nonpromotables = self._get_promotables(can_promote=False)
        #expected = None
        for name in nonpromotables:
            morph = Morph8(name)
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)

    def test_nonpromotables(self):
        """
        Maxing.
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

class FE8Promotables(Morph8TestCase):
    """
    Conduct series of tests with FE8 promotable units as subjects.
    """

    def test_get_promotion_list(self):
        """
        Assert promo-list non-empty.
        """
        promotables = self._get_promotables(can_promote=True)
        #expected = []
        for name in filter(lambda name_: name_ not in self.trainees, promotables):
            morph = Morph8(name)
            actual = morph.get_promotion_list()
            self.assertTrue(actual)

    def test_get_promotion_item(self):
        """
        Assert that for each unit, the promo-item is correct.
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

    def test_promotables(self):
        """
        Maxing.
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

class FE8Ross(Morph8TestCase):
    """
    Conduct series of tests with FE8!Ross as subject.
    """

    def test_get_promotion_list(self):
        """
        Tests output.
        """
        name = "Ross"
        self._test_get_promotion_list__trainee(name)

    def test_ross(self):
        name = "Ross"
        self._test_scrub(name)

    def test_get_promotion_item__ross(self):
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

class FE8Ross2(unittest.TestCase):
    """
    Conducts tests with FE8!Ross as subject.
    """

    def setUp(self):
        """
        Defines rudimentary Morph subclass and instance thereof also.
        """
        class TestMorph8(Morph):
            """
            A virtual representation of a unit from FE8: The Sacred Stones.
            """
            game_no = 8
        self.morph = TestMorph8("Ross", which_bases=0, which_growths=0)
        logger.critical("%s", self.id())

    def test_promote__branch_unspecified(self):
        """
        `promote` encompasses units who must choose their promotion path.
        """
        ross = self.morph
        ross.current_lv = 10
        valid_promotions = ('Fighter', 'Pirate', 'Journeyman (2)')
        with self.assertRaises(PromotionError) as err_ctx:
            ross.promote()
        (err_msg,) = err_ctx.exception.args
        self.assertIn(str(valid_promotions), err_msg)
        actual = err_ctx.exception.reason
        expected = PromotionError.Reason.INVALID_PROMOTION
        self.assertEqual(actual, expected)
        actual = err_ctx.exception.promotion_list
        expected = valid_promotions
        self.assertTupleEqual(actual, expected)

class FE8Amelia(Morph8TestCase):
    """
    Conduct series of tests with FE8!Amelia as subject.
    """

    def test_get_promotion_list__amelia(self):
        name = "Amelia"
        self._test_get_promotion_list__trainee(name)

    def test_get_promotion_item__amelia(self):
        name = "Amelia"
        promotion_item = "Knight Crest"
        self._test_get_promotion_item__trainee(name, promotion_item)

    def test_amelia(self):
        name = "Amelia"
        self._test_scrub(name)

class FE8Ewan(Morph8TestCase):
    """
    Conduct series of tests with FE8!Ewan as subject.
    """

    def test_get_promotion_list__ewan(self):
        name = "Ewan"
        self._test_get_promotion_list__trainee(name)

    def test_get_promotion_item__ewan(self):
        name = "Ewan"
        promotion_item = "Guiding Ring"
        self._test_get_promotion_item__trainee(name, promotion_item)

    def test_ewan(self):
        name = "Ewan"
        self._test_scrub(name)

    def test_metiss_tome(self):
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

    def test_as_string(self):
        morph = Morph8("Ewan")
        morph.use_metiss_tome()
        actual = morph.as_string()
        self.assertIsInstance(actual, str)
        logger.debug("as_string -> %s", actual)

class FE8Eirika(Morph8TestCase):
    """
    Conduct series of tests with FE8!Eirika as subject.
    """

    def setUp(self):
        """
        Initializes lord morph.
        """
        self.morph = Morph8("Eirika")
        super().setUp()

    def test_promote__early(self):
        """
        Asserts that Eirika can promote early.
        """
        eirika = self.morph
        self.assertLess(eirika.current_lv, 10)
        eirika.promote()
        self.assertEqual(eirika.current_clstype, "classes__promotion_gains")
        with self.assertRaises(PromotionError):
            eirika.promote()

    def test_stat_boosters(self):
        """
        Test stat-boosting functionality.
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
        eirika = self.morph
        for item, statbonus in item_bonus_dict.items():
            original_stats = eirika.current_stats.copy()
            eirika.use_stat_booster(item)
            stat, bonus = statbonus
            expected = getattr(original_stats, stat) + bonus * 100
            actual = getattr(eirika.current_stats, stat)
            self.assertEqual(actual, expected)

    def test_inventory_size(self):
        """
        Validate inventory size.
        """
        eirika = self.morph
        actual = eirika.inventory_size
        expected = 0
        self.assertEqual(actual, expected)

class FE8Ephraim(Morph8TestCase):
    """
    Conduct series of tests with FE8!Ephraim as subject.
    """

    def setUp(self):
        """
        Initializes lord morph.
        """
        self.morph = Morph8("Ephraim")
        super().setUp()

    def test_inventory_size(self):
        """
        Validates inventory size.
        """
        ephraim = self.morph
        actual = ephraim.inventory_size
        self.assertIsInstance(actual, int)
        self.assertEqual(actual, 0)

    def test_promote__early(self):
        """
        Asserts that Ephraim can promote early.
        """
        ephraim = self.morph
        self.assertLess(ephraim.current_lv, 10)
        ephraim.promote()
        self.assertEqual(ephraim.current_clstype, "classes__promotion_gains")
        with self.assertRaises(PromotionError):
            ephraim.promote()

class Morph9TestCase(unittest.TestCase):
    """
    Provides framework for testing FE9 units.
    """

    def setUp(self):
        """
        Initializes band list.
        """
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
        logger.critical("%s", self.id())

    @staticmethod
    def _get_promotables(can_promote):
        """
        Gets unit list filtered by ability to promote.
        """
        # query for list of units who cannot promote
        url_name = "path-of-radiance"
        return _get_promotables(url_name, can_promote=can_promote)

class FE9Ike(Morph9TestCase):
    """
    Conduct series of tests with FE9!Ike as subject.
    """

    def setUp(self):
        """
        Initializes morph instance.
        """
        name = "Ike"
        self.morph = Morph9(name)
        super().setUp()

    def test_inventory_size(self):
        """
        Validate inventory size
        """
        ike = self.morph
        actual = ike.inventory_size
        self.assertIsInstance(actual, int)
        self.assertGreater(actual, 0)

    def test_promote__early(self):
        """
        Show that Ike can promote early.
        """
        ike = self.morph
        self.assertLess(ike.current_lv, 10)
        ike.promote()

    def test_get_promotion_item(self):
        """
        Validate 'promo-item'
        """
        ike = self.morph
        actual = ike.get_promotion_item()
        expected = "*Chapter 18 - Start*"
        self.assertEqual(actual, expected)
        ike.promote()
        actual = ike.get_promotion_item()
        self.assertIsNone(actual)

    def test_stat_boosters(self):
        """
        Demo of stat-boosting.
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
        ike = self.morph
        for item, statbonus in item_bonus_dict.items():
            original_stats = ike.current_stats.copy()
            ike.use_stat_booster(item)
            stat, bonus = statbonus
            expected = getattr(original_stats, stat) + bonus * 100
            actual = getattr(ike.current_stats, stat)
            self.assertEqual(actual, expected)

    def test_equip_knight_ward__not_a_knight(self):
        """
        Try to equip Knight Ward.
        """
        ike = self.morph
        with self.assertRaises(KnightWardError) as err_ctx:
            ike.equip_knight_ward()
        actual = err_ctx.exception.reason
        expected = KnightWardError.Reason.NOT_A_KNIGHT
        self.assertEqual(actual, expected)

    def test_unequip_knight_ward__not_a_knight(self):
        """
        Try to unequip Knight Ward.
        """
        ike = self.morph
        with self.assertRaises(KnightWardError) as err_ctx:
            ike.unequip_knight_ward()
        actual = err_ctx.exception.reason
        expected = KnightWardError.Reason.NOT_A_KNIGHT
        self.assertEqual(actual, expected)

class FE9Volke(Morph9TestCase):
    """
    Conduct series of tests with FE9!Volke as subject.
    """

    def setUp(self):
        """
        Initializes morph instance.
        """
        name = "Volke"
        self.morph = Morph9(name)
        super().setUp()

    def test_promote(self):
        """
        Volke can promote at base-level.
        """
        volke = self.morph
        self.assertEqual(volke.current_lv, 10)
        volke.promote()

    def test_get_promotion_item(self):
        """
        Validate 'promo-item'
        """
        volke = self.morph
        actual = volke.get_promotion_item()
        expected = "*Chapter 19 - Pay Volke*"
        self.assertEqual(actual, expected)
        volke.promote()
        actual = volke.get_promotion_item()
        self.assertIsNone(actual)

class FE9Promotables(Morph9TestCase):
    """
    Conduct series of tests with FE9 promotables as subject.
    """

    def test_get_promotion_item(self):
        """
        Validate promo-item for each unit.
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

    def test_promotables(self):
        """
        Maxing.
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

    def test_get_promotion_list(self):
        """
        Assert promo-list is non-empty.
        """
        promotables = self._get_promotables(can_promote=True)
        #expected = []
        for name in promotables:
            morph = Morph9(name)
            actual = morph.get_promotion_list()
            self.assertTrue(actual)

class FE9Unpromotables(Morph9TestCase):
    """
    Conduct series of tests with FE9 unpromotables as subject.
    """

    def test_get_promotion_list__nonpromotables(self):
        """
        Assert promo-list is empty.
        """
        nonpromotables = self._get_promotables(can_promote=False)
        expected = []
        for name in nonpromotables:
            if name == "Sephiran":
                break
            morph = Morph9(name)
            actual = morph.get_promotion_list()
            self.assertListEqual(actual, expected)

    def test_get_promotion_item(self):
        """
        Validate promo-item for each unit.
        """
        nonpromotables = self._get_promotables(can_promote=False)
        #expected = None
        for name in nonpromotables:
            if name == "Sephiran":
                break
            morph = Morph9(name)
            actual = morph.get_promotion_item()
            self.assertIsNone(actual)

    def test_nonpromotables(self):
        """
        Maxing.
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
        nonpromotables = self._get_promotables(False)
        for name in nonpromotables:
            if name == "Sephiran":
                break
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

class FE9Knight(Morph9TestCase):
    """
    Conduct series of tests with a FE9 knight as subject.
    """

    def setUp(self):
        """
        Initializes morph instance.
        """
        name = "Kieran"
        self.morph = Morph9(name)
        super().setUp()

    def test_inventory_size(self):
        """
        Validate inventory size.
        """
        kieran = self.morph
        actual = kieran.inventory_size
        expected = 8
        self.assertEqual(actual, expected)

    def test_equip_knight_ward__no_space(self):
        """
        Try to equip Knight Ward without any free space.
        """
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

    def test_unequip_knight_ward(self):
        """
        Try to unequip Knight Ward that morph hasn't got on.
        """
        kieran = self.morph
        with self.assertRaises(KnightWardError):
            kieran.unequip_knight_ward()
        kieran.equipped_bands = {"Knight Ward": None}
        kieran.knight_ward_is_equipped = True
        kieran.unequip_knight_ward()
        actual = kieran.knight_ward_is_equipped
        self.assertIs(actual, False)
        actual = kieran.equipped_bands
        self.assertDictEqual(actual, {})
        self.assertEqual(kieran.growth_rates, kieran._og_growth_rates)

    def test_equip_knight_ward(self):
        """
        Successful equipping of Knight Ward.
        """
        # initialize
        kieran = self.morph
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


class FE9BandEquipper(Morph9TestCase):
    """
    Conduct series of tests with a FE9 unit who can equip a band as subject.
    """

    def setUp(self):
        """
        Initializes morph instance.
        """
        name = "Jill"
        self.morph = Morph9(name)
        super().setUp()

    def test_equip_band(self):
        """
        Test equipping of band.
        """
        jill = self.morph
        band_name = self.bands[0]
        og_growths = jill.growth_rates.copy()
        jill.equip_band(band_name)
        self.assertIn(band_name, jill.equipped_bands)
        self.assertEqual(len(jill.equipped_bands), 1)
        new_growths = jill.growth_rates
        actual = all(og_growths == new_growths)
        expected = False
        self.assertIs(actual, expected)
        with self.assertRaises(BandError) as err_ctx:
            jill.equip_band(band_name)
        actual = err_ctx.exception.reason
        expected = BandError.Reason.ALREADY_EQUIPPED
        self.assertEqual(actual, expected)

    def test_level_up__with_band(self):
        """
        Test level-up with band on.
        """
        jill = self.morph
        bands = self.bands
        for i in range(3):
            band = bands[i]
            jill.equip_band(band)
        jill.unequip_band(band)
        with self.assertRaises(BandError) as err_ctx:
            jill.unequip_band("")
        err = err_ctx.exception
        actual = err.reason
        expected = BandError.Reason.NOT_EQUIPPED
        self.assertEqual(actual, expected)
        actual = err.absent_band
        expected = ""
        self.assertEqual(actual, expected)
        first_band = bands[0]
        with self.assertRaises(BandError) as err_ctx:
            jill.equip_band(first_band)
        err = err_ctx.exception
        actual = err.reason
        expected = BandError.Reason.ALREADY_EQUIPPED
        self.assertEqual(actual, expected)
        actual = err.equipped_band
        expected = first_band
        self.assertEqual(actual, expected)
        with self.assertRaises(BandError) as err_ctx:
            jill.equip_band("")
        err = err_ctx.exception
        actual = err.reason
        expected = BandError.Reason.NOT_FOUND
        self.assertEqual(actual, expected)
        actual = err.valid_bands
        logger.debug("valid_bands: %s", actual)
        expected = ['Sword Band', 'Soldier Band', 'Fighter Band', 'Archer Band', 'Knight Band', 'Paladin Band', 'Pegasus Band', 'Wyvern Band', 'Mage Band', 'Priest Band', 'Thief Band']
        self.assertListEqual(actual, expected)
        jill.level_up(10)
        jill2 = Morph9("Jill")
        jill2.level_up(10)
        logger.debug("%r", jill > jill2)

    def test_equip_band__exceed_inventory_space(self):
        """
        Try to equip band without any space to hold it.
        """
        # equip bands
        jill = self.morph
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
        Try to equip invalid band to hold it.
        """
        band_name = ""
        jill = self.morph
        og_growths = jill.growth_rates.copy()
        with self.assertRaises(BandError) as err_ctx:
            jill.equip_band(band_name)
        # check error
        actual = err_ctx.exception.reason
        expected = BandError.Reason.NOT_FOUND
        self.assertEqual(actual, expected)
        # check state
        self.assertNotIn(band_name, jill.equipped_bands)
        self.assertEqual(len(jill.equipped_bands), 0)
        new_growths = jill.growth_rates
        actual = all(og_growths == new_growths)
        expected = True
        self.assertIs(actual, expected)

class GetMorph(unittest.TestCase):
    """
    Tests `get_morph` shortcut function on a few test cases.
    """

    def setUp(self):
        """
        Adds test-id to log for demarcation
        """
        logger.critical("%s", self.id())

    def test_roy(self):
        """
        Roy
        """
        roy = get_morph(6, "Roy")
        actual = "Roy"
        expected = roy.name
        self.assertEqual(actual, expected)

    def test_error_propagated_from_morph(self):
        """
        FE6!Marth
        """
        with self.assertRaises(UnitNotFoundError) as err_ctx:
            get_morph(6, "Marth")
        #actual = err_ctx.exception.unit_type
        #expected = UnitNotFoundError.UnitType.NORMAL
        #self.assertEqual(actual, expected)

    def test_invalid_game(self):
        """
        For FE games excluding 4-9.
        """
        lords_and_games = {
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
        for game_no in range(4, 10):
            lords_and_games.pop(game_no)
        for game, lord in lords_and_games.items():
            with self.assertRaises(NotImplementedError):
                get_morph(game, lord)

class ReprTestCases(unittest.TestCase):
    """
    Shows REPR of various Morphs.
    """

    def setUp(self):
        """
        Adds test-id to log for demarcation
        """
        logger.critical("%s", self.id())
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

    def test_repr(self):
        """
        Shows REPR for lord of each game.
        """
        for game_no in range(4, 10):
            lord = self.lords_and_games[game_no]
            morph = get_morph(game_no, lord)
            logger.debug("\n\n%s\n", morph)

    def test_gba_promoted(self):
        """
        Shows REPR for promoted lord of each GBA game.
        """
        for game_no in range(6, 9):
            lord = self.lords_and_games[game_no]
            morph = get_morph(game_no, lord)
            morph.use_stat_booster("Energy Ring")
            morph.level_up(20 - morph.current_lv)
            morph.promote()
            morph.use_stat_booster("Angelic Robe")
            logger.debug("\n\n%s\n", morph)

    def test_lyn_mode(self):
        """
        Shows REPR for lyn_mode character from FE7.
        """
        morph = get_morph(7, "Florina", lyn_mode=True)
        morph.level_up(20 - morph.current_lv)
        morph.promote()
        logger.debug("\n\n%s\n", morph)

    def test_trainee(self):
        """
        Shows REPR for trainee character from FE8.
        """
        morph = get_morph(8, "Amelia")
        morph.level_up(10 - morph.current_lv)
        morph.promo_cls = "Cavalier (F)"
        morph.promote()
        morph.level_up(20 - morph.current_lv)
        morph.promo_cls = "Paladin (F)"
        morph.promote()
        logger.debug("\n\n%s\n", morph)

    def test_gba_hard_mode(self):
        """
        Shows REPR for hard-mode character from FE6.
        """
        rutger = get_morph(6, "Rutger", hard_mode=True)
        rutger.level_up(20 - rutger.current_lv)
        rutger.promote()
        logger.debug("\n\n%s\n", rutger)

    def test_as_string__gba_growths_item(self):
        """
        Shows REPR for Afa's Drops character from FE8.
        """
        heath = get_morph(7, "Heath", hard_mode=True)
        heath.use_afas_drops()
        heath.level_up(20 - heath.current_lv)
        heath.promote()
        heath.use_stat_booster("Speedwings")
        logger.debug("\n\n%s\n", heath.as_string())

    def test_genealogy_kid(self):
        """
        Shows REPR for promoted Genealogy kid.
        """
        larcei = get_morph(4, "Lakche", father="Lex")
        larcei.level_up(20 - larcei.current_lv)
        larcei.promote()
        logger.debug("\n\n%s\n", larcei)

    def test_thracia_unit_with_scroll(self):
        """
        Shows REPR for FE5 unit with scroll on.
        """
        asvel = get_morph(5, "Asvel")
        asvel.level_up(20 - asvel.current_lv)
        asvel.equip_scroll("Blaggi")
        asvel.equip_scroll("Odo")
        logger.debug("\n\n%s\n", asvel)

    def test_radiant_unit_with_band(self):
        """
        Shows REPR for FE9 unit with band on.
        """
        morph = get_morph(9, "Oscar")
        morph.equip_band("Thief Band")
        morph.equip_knight_ward()
        morph.level_up(20 - morph.current_lv)
        logger.debug("\n\n%s\n", morph)

    def test_early_promo_lord(self):
        """
        Shows REPR for FE7 unit who promoted early.
        """
        morph = get_morph(7, "Hector")
        #morph.level_up(20 - morph.current_lv)
        morph.promote()
        logger.debug("\n\n%s\n", morph)

class GtTestCases(unittest.TestCase):
    """
    Shows REPR of gt of various Morphs.
    """

    def test_gt__christmas_cavaliers(self):
        """
        Shows REPR for unit comparison of XMas Cavaliers.
        """
        morph1 = Morph6("Allen")
        morph2 = Morph6("Lance")
        actual = (morph1 > morph2).__str__()
        logger.debug("\n\n%s\n", actual)

    def test_gt__hm_and_nonhm(self):
        """
        Shows REPR for comparison of a unit across difficulties.
        """
        morph1 = Morph6("Rutger", hard_mode=True)
        morph2 = Morph6("Marcus")
        actual = (morph1 > morph2).__str__()
        logger.debug("\n\n%s\n", actual)

    def test_gt__genealogykid_and_adult(self):
        """
        Shows REPR for comparison of two units with differing attributes.
        """
        morph1 = Morph4("Lakche", father="Lex")
        morph2 = Morph4("Sigurd")
        actual = (morph1 > morph2).__str__()
        logger.debug("\n\n%s\n", actual)

'''
Morph4Tests = unittest.TestSuite(
    [
        FE4Ayra,
        Morph4Class,
        FE4Deirdre,
        FE4UnpromotedUnit,
        FE4Nonpromotables,
        FE4Promotables,
        FE4PromotedUnit,
        FE4ChildUnit,
    ]
)
Morph5Tests = unittest.TestSuite(
    [
        FE5Promotables,
        FE5Unpromotables,
        FE5Leif,
        FE5Linoan,
        FE5Lara,
        FE5PromotedUnit,
        FE5Eda,
    ]
)
Morph6Tests = unittest.TestSuite(
    [
        Morph6Class2,
        FE6Rutger,
        FE6Roy,
        Morph6TestCase,
        Morph6Class,
        FE6Gonzales,
        FE6Unpromotables,
        FE6Promotables,
        FE6Rutger,
        FE6Roy,
        FE6Hugh,
    ]
)
Morph7Tests = unittest.TestSuite(
    [
        Morph7Class,
        FE7Ninian,
        FE7Hector,
        FE7Eliwood,
        FE7Nino,
        FE7Unpromotables,
        FE7Promotables,
        FE7HardModeUnit,
        FE7NormalOnlyUnit,
        FE7NonLyndisLeague,
        FE7LyndisLeague,
        FE7Wallace,
    ]
)
Morph8Tests = unittest.TestSuite(
    [
        Morph8TestCase,
        FE8Unpromotables,
        FE8Promotables,
        FE8Ross,
        FE8Ross2,
        FE8Amelia,
        FE8Ewan,
        FE8Eirika,
        FE8Ephraim,
    ]
)
Morph9Tests = unittest.TestSuite(
    [
        FE9Ike,
        FE9Volke,
        FE9Promotables,
        FE9Unpromotables,
        FE9Knight,
        FE9BandEquipper,
    ]
)
'''
