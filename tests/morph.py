"""
"""

import sqlite3
import unittest
import enum

from aenir.games import FireEmblemGame
from aenir.morph import (
    BaseMorph,
    Morph,
)

# TODO
# subclass BaseMorph
# test: GAME, STATS, query_db, lookup

class BaseMorphTest(unittest.TestCase):
    """
    """

    class TestMorph(BaseMorph):
        """
        """

    def setUp(self):
        """
        """

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
        fields = ("HP", "Def")
        filters = {"Name": "Rutger"}
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

