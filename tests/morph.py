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
)

configure_logging()

class BaseMorphTest(unittest.TestCase):
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

class MorphTest(unittest.TestCase):
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

            @classmethod
            def GAME(cls):
                """
                """
                return FireEmblemGame(cls.game_no)

        self.TestMorph = TestMorph6
        self.TestMorph.__name__ = "Morph"

    @unittest.skip("User is outright forbidden from instantiating generic Morph instances.")
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
        self.assertEqual(rutger.unit, "Rutger")
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
            },
        )

    def test_init__unit_dne(self):
        """
        """
        with self.assertRaises(ValueError):
            marth = self.TestMorph("Marth", which_bases=0, which_growths=0)

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

