"""
"""

import unittest
import logging

from aenir.stats import (
    AbstractStats,
    GenealogyStats,
    ThraciaStats,
    GBAStats,
)
from aenir.logging import logger

# TODO: refactor s.t. dummy subclass is used instead of implemented one.
# TODO: Pare down on list of fields in  source files.

class AbstractStatsTests(unittest.TestCase):
    """
    Demo of how 'STAT_LIST' should be implemented to be a valid subclass of
    AbstractStats.
    """

    class NoStatListStats(AbstractStats):
        """
        Where 'STAT_LIST' class method is not implemented.
        """

    class NonTupleStats(AbstractStats):
        """
        Where 'STAT_LIST' does not return tuple.
        """

        @classmethod
        def STAT_LIST(cls):
            """
            Returns non-tuple.
            """
            return None

    class NonStrTupleStats(AbstractStats):
        """
        Where 'STAT_LIST' is a tuple containing at least one str.
        """

        @classmethod
        def STAT_LIST(cls):
            """
            Returns non-tuple.
            """
            return (
                "a",
                "b",
                3,
                "c",
            )

    class InvalidIdentifierStats(AbstractStats):
        """
        Where 'STAT_LIST' is a str-tuple containing one invalid identifier.
        """

        @classmethod
        def STAT_LIST(cls):
            """
            Returns tuple of strings that cannot be used as Python identifiers.
            """
            return (
                "a",
                "b",
                ".",
            )

    #@unittest.skip( "Apparently, attributes can be assigned invalid identifiers, but they'll be hidden.")
    def test_STAT_LIST_must_have_valid_identifiers(self):
        """
        Asserts that 'STAT_LIST' class method must return tuple.
        """
        test_class = self.InvalidIdentifierStats
        stat_dict = test_class.get_stat_dict(0)
        #with self.assertRaises(AttributeError) as assert_err:
        test_obj = test_class(**stat_dict)
        test_obj_period = getattr(test_obj, ".")
        logger.warning(
            "Hidden attribute has been defined: getattr(%s(**%s)., '.') = %d",
            test_class.__name__, stat_dict, test_obj_period,
        )

    def test_STAT_LIST_must_be_tuple_of_strings(self):
        """
        Asserts that 'STAT_LIST' class method must return str-tuple.
        """
        test_class = self.NonStrTupleStats
        stat_dict = test_class.get_stat_dict(0)
        #with self.assertRaises(AttributeError) as assert_err:
        with self.assertRaises(TypeError) as assert_err:
            test_obj = test_class(**stat_dict)

    def test_STAT_LIST_must_be_tuple(self):
        """
        Asserts that 'STAT_LIST' class method must return tuple.
        """
        with self.assertRaises(AssertionError) as assert_err:
            self.NonTupleStats()

    def test_cannot_initialize(self):
        """
        Asserts that subclasses that have not implemented the 'STAT_LIST' class
        method cannot be used to create an object.
        """
        with self.assertRaises(TypeError) as type_err:
            self.NoStatListStats()

class StatsTests(unittest.TestCase):
    """
    Demo of methods of a functional subclass of AbstractStats.
    """

    class FunctionalStats(AbstractStats):
        """
        Functional in that the 'STAT_LIST' class method is defined.
        """
        @classmethod
        def STAT_LIST(cls):
            """
            Returns tuple of strings that can be used as Python identifiers.
            """
            return (
                "a",
                "b",
                "c",
                "d",
                "e",
                "f",
                "g",
            )

    def setUp(self):
        """
        Initializes minimal kwargs for initialization of FunctionalStats.
        """
        self.stats_class = self.FunctionalStats
        self.init_kwargs = {
            "a": 0,
            "b": 0,
            "c": 0,
            "d": 0,
            "e": 0,
            "f": 0,
            "g": 0,
        }

    def test_get_stat_dict__eq_stat_list(self):
        """
        Tests that key-set in stat-dict is identical to STAT_LIST.
        """
        actual = set(self.stats_class.get_stat_dict(0))
        expected = set(self.stats_class.STAT_LIST())
        self.assertSetEqual(actual, expected)

    def test_get_stat_dict(self):
        """
        Tests that key-set in stat-dict is identical to stats listed in setUp.
        """
        actual = set(self.stats_class.get_stat_dict(0))
        expected = set(self.init_kwargs)
        self.assertSetEqual(actual, expected)

    def test_init__missing_kwarg(self):
        """
        """
        kwargs = self.init_kwargs
        hp = kwargs.pop('a')
        test_class = self.stats_class
        with self.assertRaises(TypeError) as type_err:
            test_class(**kwargs)

    def test_init__unexpected_kwarg(self):
        """
        """
        stat_dict = self.init_kwargs
        stat_dict['unexpected_kwarg'] = None
        #with self.assertLogs(logger, logging.CRITICAL) as log_ctx:
        test_class = self.stats_class
        with self.assertLogs(logger, logging.WARNING) as log_ctx:
            stats_obj = test_class(**stat_dict)


class ImplementedStatsTests(unittest.TestCase):
    """
    Tests that subclasses contain the expected stat-attributes.
    """

    def test_genealogy_stats(self):
        """
        Stats with growth rates in FE4: Genealogy of the Holy War.
        """
        expected = (
            "HP",
            "Str",
            "Mag",
            "Skl",
            "Spd",
            "Lck",
            "Def",
            "Res",
        )
        actual = GenealogyStats.STAT_LIST()
        self.assertTupleEqual(actual, expected)

    def test_gba_stats(self):
        """
        Stats with growth rates in FE6-8.
        """
        expected = (
            "HP",
            "Pow",
            "Skl",
            "Spd",
            "Lck",
            "Def",
            "Con",
            "Mov",
        )
        actual = GBAStats.STAT_LIST()
        self.assertTupleEqual(actual, expected)

    def test_thracia_stats(self):
        """
        Stats with growth rates in FE5: Thracia 776.
        """
        expected = (
            "HP",
            "Str",
            "Mag",
            "Skl",
            "Spd",
            "Lck",
            "Def",
            "Con",
            "Mov",
        )
        actual = ThraciaStats.STAT_LIST()
        self.assertTupleEqual(actual, expected)
