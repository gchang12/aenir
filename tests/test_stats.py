"""
Demo of how 'STAT_LIST' should be implemented to be a valid subclass of AbstractStats.
"""

import unittest
import logging

from aenir.stats import (
    AbstractStats,
    GenealogyStats,
    ThraciaStats,
    RadiantStats,
    GBAStats,
)
from aenir._logging import (
    configure_logging,
    logger,
    time_logger,
)

configure_logging()
time_logger.critical("")

class IntStatsTest(unittest.TestCase):
    """
    Demo of methods of a functional int-based subclass of AbstractStats.
    """

    def setUp(self):
        """
        Initializes minimal kwargs for initialization of FunctionalStats2?, which are defined here also.
        """

        class FunctionalStats(AbstractStats):
            """
            Functional in that the 'STAT_LIST' class method is defined.
            """

            @staticmethod
            def STAT_LIST():
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

            @staticmethod
            def ZERO_GROWTH_STAT_LIST():
                """
                """
                return ()

        class FunctionalStats2(AbstractStats):
            """
            Functional in that the 'STAT_LIST' class method is defined. Exists to
            demonstrate that stats of different classes cannot be operated on even if
            they share the same 'STAT_LIST'.
            """
            @staticmethod
            def STAT_LIST():
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

            @staticmethod
            def ZERO_GROWTH_STAT_LIST():
                """
                Returns empty tuple.
                """
                return ()

        self.FunctionalStats = FunctionalStats
        self.FunctionalStats2 = FunctionalStats2
        self.statdict1 = {
            "a": 18,
            "b": 7,
            "c": 5,
            "d": 9,
            "e": 2,
            "f": 5,
            "g": 1,
        }
        self.statdict2 = {
            "a": 1,
            "b": 8,
            "c": 2,
            "d": 10,
            "e": 1,
            "f": 8,
            "g": 0,
        }
        logger.critical("%s", self.id())

    def test_repr(self):
        """
        Prints repr of stats to log-report.
        """
        stats = self.FunctionalStats(**self.statdict1)
        logger.debug("\n%r", stats)

    def test_repr1(self):
        """
        Validates repr of stats.
        """
        init_kwargs = {
            "a": 18,
            "b": 7,
            "c": 5,
            "d": 9,
            "e": 2,
            "f": 5,
            "g": 1,
        }
        stats = self.FunctionalStats(**init_kwargs)
        expected = '''FunctionalStats
===============
   a: 18.00
   b:  7.00
   c:  5.00
   d:  9.00
   e:  2.00
   f:  5.00
   g:  1.00'''
        actual = stats.__repr__()
        self.assertEqual(actual, expected)

    def test_sum(self):
        """
        Tests sum method.
        """
        statdict = {
            "a": 18,
            "b": 7,
            "c": 5,
            "d": 9,
            "e": 2,
            "f": 5,
            "g": 1,
        }
        stats = self.FunctionalStats(**statdict)
        expected = sum(statdict.values()) * 100
        actual = sum(stats)
        self.assertEqual(actual, expected)

    def test_as_list(self):
        """
        Tests as_list method.
        """
        stats = self.FunctionalStats(**self.statdict2)
        expected = [(stat, value * 100) for stat, value in self.statdict2.items()]
        actual = stats.as_list()
        self.assertListEqual(actual, expected)

    def test_as_dict(self):
        """
        Tests as_dict method.
        """
        stats = self.FunctionalStats(**self.statdict2)
        expected = {stat: value * 100 for stat, value in self.statdict2.items()}
        actual = stats.as_dict()
        self.assertDictEqual(actual, expected)

    def test_copy(self):
        """
        Tests copy method.
        """
        stat_dict = self.statdict1
        expected = self.FunctionalStats(**stat_dict)
        actual = expected.copy()
        for key in stat_dict:
            expected_val = getattr(expected, key)
            actual_val = getattr(actual, key)
            self.assertEqual(actual_val, expected_val)

    def test_mul(self):
        """
        Tests mul method.
        """
        stat_dict = {
            "a": 18,
            "b": 7,
            "c": 5,
            "d": 9,
            "e": 2,
            "f": 5,
            "g": 1,
        }
        stat_dict3 = {}
        for key, val in stat_dict.items():
            stat_dict3[key] = val * 3
        expected = self.FunctionalStats(**stat_dict3)
        actual = self.FunctionalStats(**stat_dict) * 3
        for key in stat_dict:
            expected_val = getattr(expected, key)
            actual_val = getattr(actual, key)
            self.assertEqual(actual_val, expected_val)

    def test_eq__type_mismatch(self):
        """
        Tests eq method.
        """
        stats1 = self.FunctionalStats(**self.statdict1)
        stats2 = self.FunctionalStats2(**self.statdict1)
        with self.assertRaises(TypeError):
            stats1 == stats2

    def test_add(self):
        """
        Tests add method.
        """
        new_statdict = {}
        statlist = tuple(self.statdict1)
        for stat in statlist:
            new_statdict[stat] = self.statdict1[stat] + self.statdict2[stat]
        expected = self.FunctionalStats(**new_statdict)
        summand1 = self.FunctionalStats(**self.statdict1)
        summand2 = self.FunctionalStats(**self.statdict2)
        actual = summand1 + summand2
        stats_are_equal = []
        for stat in statlist:
            actual_val = getattr(actual, stat)
            expected_val = getattr(expected, stat)
            stats_are_equal.append(actual_val == expected_val)
        self.assertIs(all(stats_are_equal), True)

    def test_eq__all_matching(self):
        """
        Tests eq method.
        """
        stats1 = self.FunctionalStats(**self.statdict1)
        stats2 = self.FunctionalStats(**self.statdict1)
        actual = all(stats1 == stats2)
        expected = True
        self.assertIs(actual, expected)

    def test_eq__not_all_matching(self):
        """
        Tests eq method.
        """
        stats1 = self.FunctionalStats(**self.statdict1)
        self.statdict1['a'] = 99
        stats2 = self.FunctionalStats(**self.statdict1)
        actual = all(stats1 == stats2)
        expected = False
        self.assertIs(actual, expected)
        stats1.a = 9900
        expected = True
        actual = all(stats1 == stats2)
        self.assertIs(actual, expected)

    def test_imin(self):
        """
        Tests that imin sets calling stats of calling object to minimum of self's
        attributes and other's.
        """
        stats1 = self.FunctionalStats(**self.statdict1)
        stats2 = self.FunctionalStats(**self.statdict2)
        expected_stats = self.FunctionalStats(
            multiplier=1,
            **{
                "a": min(stats1.a, stats2.a),
                "b": min(stats1.b, stats2.b),
                "c": min(stats1.c, stats2.c),
                "d": min(stats1.d, stats2.d),
                "e": min(stats1.e, stats2.e),
                "f": min(stats1.f, stats2.f),
                "g": min(stats1.g, stats2.g),
            }
        )
        stats1.imin(stats2)
        actual_stats = stats1
        for attrname in ("a", "b", "c", "d", "e", "f", "g"):
            actual = getattr(actual_stats, attrname)
            expected = getattr(expected_stats, attrname)
            self.assertEqual(actual, expected)

    def test_imax(self):
        """
        Tests that imax sets calling stats of calling object to minimum of self's
        attributes and other's.
        """
        stats1 = self.FunctionalStats(**self.statdict1)
        stats2 = self.FunctionalStats(**self.statdict2)
        expected_stats = self.FunctionalStats(
            multiplier=1,
            **{
                "a": max(stats1.a, stats2.a),
                "b": max(stats1.b, stats2.b),
                "c": max(stats1.c, stats2.c),
                "d": max(stats1.d, stats2.d),
                "e": max(stats1.e, stats2.e),
                "f": max(stats1.f, stats2.f),
                "g": max(stats1.g, stats2.g),
            }
        )
        stats1.imax(stats2)
        actual_stats = stats1
        for attrname in ("a", "b", "c", "d", "e", "f", "g"):
            actual = getattr(actual_stats, attrname)
            expected = getattr(expected_stats, attrname)
            self.assertEqual(actual, expected)

    def test_imax__different_classes(self):
        """
        Tests that imax only works for Stats objects of same type, even if the
        STAT_LIST methods return identical tuples.
        """
        stats1 = self.FunctionalStats(**self.statdict1)
        stats2 = self.FunctionalStats2(**self.statdict2)
        self.assertTupleEqual(stats1.STAT_LIST(), stats2.STAT_LIST())
        with self.assertRaises(TypeError):
            stats1.imax(stats2)
        with self.assertRaises(TypeError):
            stats2.imax(stats1)

    def test_imin__different_classes(self):
        """
        Tests that imin only works for Stats objects of same type, even if the
        STAT_LIST methods return identical tuples.
        """
        stats1 = self.FunctionalStats(**self.statdict1)
        stats2 = self.FunctionalStats2(**self.statdict2)
        self.assertTupleEqual(stats1.STAT_LIST(), stats2.STAT_LIST())
        with self.assertRaises(TypeError):
            stats1.imin(stats2)
        with self.assertRaises(TypeError):
            stats2.imin(stats1)

    def test_iadd(self):
        """
        Tests that the Stats object is incremented.
        """
        expected_stats = self.FunctionalStats(
            **{
                "a": 19,
                "b": 15,
                "c": 7,
                "d": 19,
                "e": 3,
                "f": 13,
                "g": 1,
            }
        )
        stats1 = self.FunctionalStats(**self.statdict1)
        stats2 = self.FunctionalStats(**self.statdict2)
        self.assertIsNotNone(stats1)
        stats1 += stats2
        actual_stats = stats1
        for attrname in ("a", "b", "c", "d", "e", "f", "g"):
            actual = getattr(actual_stats, attrname)
            expected = getattr(expected_stats, attrname)
            self.assertEqual(actual, expected)

    def test_iadd__different_classes(self):
        """
        Asserts that iadd method fails if operands are of different Stats
        classes, and even if the STAT_LIST for both are identical.
        """
        # copy-paste to lt
        stats1 = self.FunctionalStats(**self.statdict1)
        stats2 = self.FunctionalStats2(**self.statdict2)
        self.assertTupleEqual(stats1.STAT_LIST(), stats2.STAT_LIST())
        with self.assertRaises(TypeError):
            stats1.__iadd__(stats2)
        with self.assertRaises(TypeError):
            stats2.__iadd__(stats1)

    def test_get_stat_dict__eq_stat_list(self):
        """
        Tests that key-set in stat-dict is identical to STAT_LIST.
        """
        actual = set(self.FunctionalStats.get_stat_dict(0))
        expected = set(self.FunctionalStats.STAT_LIST())
        self.assertSetEqual(actual, expected)

    def test_get_stat_dict(self):
        """
        Tests that key-set in stat-dict is identical to stats listed.
        """
        actual = set(self.FunctionalStats.get_stat_dict(0))
        expected = set(self.statdict1)
        self.assertSetEqual(actual, expected)

    def test_init__missing_kwarg(self):
        """
        Asserts raising of AttributeError if an attempt to initialize a stat-list without all fields is made.
        """
        kwargs = self.statdict1
        hp = kwargs.pop('a')
        with self.assertRaises(AttributeError) as type_err:
            self.FunctionalStats(**kwargs)

    def test_init__unexpected_kwarg(self):
        """
        Asserts logger-warning if attempt to initialize a stat-list with invalid field is made.
        """
        stat_dict = self.statdict1
        stat_dict['unexpected_kwarg'] = None
        #with self.assertLogs(logger, logging.CRITICAL) as log_ctx:
        with self.assertLogs(logger, logging.WARNING) as log_ctx:
            stats_obj = self.FunctionalStats(**stat_dict)

    def test_str(self):
        """
        Prints str-dunder of class to log-report.
        """
        kwargs = self.statdict1
        stats = self.FunctionalStats(**kwargs)
        actual = stats.__str__()
        logger.debug("actual: %s", actual)

    def test_add__type_error(self):
        """
        Asserts raising of type error if addition of two Stats object is attempted.
        """
        kwargs = self.statdict1
        stats1 = self.FunctionalStats(**kwargs)
        stats2 = self.FunctionalStats2(**kwargs)
        with self.assertRaises(TypeError):
            stats1 + stats2

    def test_sub__type_error(self):
        """
        Asserts raising of type error if subtraction of two Stats object is attempted.
        """
        kwargs = self.statdict1
        stats1 = self.FunctionalStats(**kwargs)
        stats2 = self.FunctionalStats2(**kwargs)
        with self.assertRaises(TypeError):
            stats1 - stats2

class ImplementedStatsTests(unittest.TestCase):
    """
    Tests that subclasses contain the expected stat-attributes.
    """

    def setUp(self):
        """
        Logs test-id for demarcation of log-lines in report.
        """
        logger.critical("%s", self.id())

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
            "Res",
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
            "Lead",
            "MS",
            "PC",
        )
        actual = ThraciaStats.STAT_LIST()
        self.assertTupleEqual(actual, expected)

class NonTupleStatsTest(unittest.TestCase):
    """
    Inspects behavior for Stats subclasses with non-tuple `STAT_LIST` values.
    """

    def setUp(self):
        """
        Logs test-id for demarcation of log-lines in report.
        """
        logger.critical("%s", self.id())

        class NonTupleStats(AbstractStats):
            """
            Where 'STAT_LIST' returns a non-tuple.
            """

            @staticmethod
            def STAT_LIST():
                """
                Returns non-tuple.
                """
                return None

            @staticmethod
            def ZERO_GROWTH_STAT_LIST():
                """
                Defines list of stats that cannot grow.
                """
                return ()

        self.Stats = NonTupleStats

    def test_STAT_LIST_must_be_tuple(self):
        """
        Asserts that 'STAT_LIST' class method must return tuple.
        """
        with self.assertRaises(NotImplementedError) as assert_err:
            self.Stats()

class NoStatListStatTest(unittest.TestCase):
    """
    Inspects behavior for Stats subclasses with unimplemented `STAT_LIST` method.
    """

    def setUp(self):
        """
        Logs test-id for demarcation of log-lines in report.
        """
        logger.critical("%s", self.id())

        class NoStatListStats(AbstractStats):
            """
            Where 'STAT_LIST' class method is not implemented.
            """

        self.Stats = NoStatListStats

    def test_cannot_initialize(self):
        """
        Asserts that subclasses that have not implemented the 'STAT_LIST' class
        method cannot be used to create an object.
        """
        with self.assertRaises(TypeError) as type_err:
            self.Stats()

class InvalidIdentifierStatsTest(unittest.TestCase):
    """
    Inspects behavior for Stats subclasses with invalid stat str-fields.
    """

    def setUp(self):
        """
        Logs test-id for demarcation of log-lines in report.
        """
        logger.critical("%s", self.id())

        class InvalidIdentifierStats(AbstractStats):
            """
            Where 'STAT_LIST' is a str-tuple containing one invalid identifier.
            """

            @staticmethod
            def STAT_LIST():
                """
                Returns tuple of strings that cannot be used as Python identifiers.
                """
                return (
                    "a",
                    "b",
                    ".",
                )

            @staticmethod
            def ZERO_GROWTH_STAT_LIST():
                """
                Defines list of stats that cannot grow.
                """
                return ()

        self.Stats = InvalidIdentifierStats

    def test_STAT_LIST_must_have_valid_identifiers(self):
        """
        Asserts that 'STAT_LIST' class method must return tuple.
        """
        stat_dict = self.Stats.get_stat_dict(0)
        #with self.assertRaises(AttributeError) as assert_err:
        test_obj = self.Stats(**stat_dict)
        test_obj_period = getattr(test_obj, ".")
        logger.debug(
            "Hidden attribute has been defined: getattr(%s(**%s)., '.') = %d",
            self.Stats.__name__, stat_dict, test_obj_period,
        )


class NonStrTupleStatsTest(unittest.TestCase):
    """
    Inspects behavior for Stats subclasses with stat fields that are invalid because of type.
    """

    def setUp(self):
        """
        Logs test-id for demarcation of log-lines in report.
        """
        logger.critical("%s", self.id())

        class NonStrTupleStats(AbstractStats):
            """
            Where 'STAT_LIST' is a tuple containing at least one str.
            """

            @staticmethod
            def STAT_LIST():
                """
                Returns a tuple containing at least one non-str.
                """
                return (
                    "a",
                    "b",
                    3,
                    "c",
                )

            @staticmethod
            def ZERO_GROWTH_STAT_LIST():
                """
                Defines list of stats that cannot grow.
                """
                return ()

        self.Stats = NonStrTupleStats

    def test_STAT_LIST_must_be_tuple_of_strings(self):
        """
        Asserts that 'STAT_LIST' class method must return str-tuple.
        """
        stat_dict = self.Stats.get_stat_dict(0)
        #with self.assertRaises(AttributeError) as assert_err:
        with self.assertRaises(TypeError) as assert_err:
            test_obj = self.Stats(**stat_dict)

