"""
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

class StatsTests(unittest.TestCase):
    """
    Demo of methods of a functional subclass of AbstractStats.
    """

    def setUp(self):
        """
        Initializes minimal kwargs for initialization of FunctionalStats.
        """
        self.init_kwargs = {
            "a": 0,
            "b": 0,
            "c": 0,
            "d": 0,
            "e": 0,
            "f": 0,
            "g": 0,
        }
        # 1.odd > 2.odd; 1.even > 2.even
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
                """
                return ()

        self.stats_class = FunctionalStats
        self.FunctionalStats = FunctionalStats
        self.FunctionalStats2 = FunctionalStats2

    def test_repr(self):
        """
        """
        stats = self.stats_class(**self.init_kwargs)
        logger.debug("\n%r", stats)

    def test_sum(self):
        """
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
        stats = self.stats_class(**statdict)
        expected = sum(statdict.values())
        actual = sum(stats)
        self.assertEqual(actual, expected)

    def test_as_list(self):
        """
        """
        expected = list(self.statdict2.items())
        stats = self.stats_class(**self.statdict2)
        actual = stats.as_list()
        self.assertListEqual(actual, expected)

    def test_as_dict(self):
        """
        """
        expected = self.statdict2
        stats = self.stats_class(**expected)
        actual = stats.as_dict()
        self.assertDictEqual(actual, expected)

    def test_copy(self):
        """
        """
        stat_dict = self.statdict1
        expected = self.stats_class(**stat_dict)
        actual = expected.copy()
        for key in stat_dict:
            expected_val = getattr(expected, key)
            actual_val = getattr(actual, key)
            self.assertEqual(actual_val, expected_val)

    def test_mul(self):
        """
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
        expected = self.stats_class(**stat_dict3)
        actual = self.stats_class(**stat_dict) * 3
        for key in stat_dict:
            expected_val = getattr(expected, key)
            actual_val = getattr(actual, key)
            self.assertEqual(actual_val, expected_val)

    def test_eq__type_mismatch(self):
        """
        """
        stats1 = self.FunctionalStats(**self.init_kwargs)
        stats2 = self.FunctionalStats2(**self.init_kwargs)
        with self.assertRaises(TypeError):
            stats1 == stats2

    def test_add(self):
        """
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
        """
        stats1 = self.FunctionalStats(**self.init_kwargs)
        stats2 = self.FunctionalStats(**self.init_kwargs)
        actual = all(stats1 == stats2)
        expected = True
        self.assertIs(actual, expected)

    def test_eq__not_all_matching(self):
        """
        """
        stats1 = self.FunctionalStats(**self.init_kwargs)
        self.init_kwargs['a'] = 99
        stats2 = self.FunctionalStats(**self.init_kwargs)
        actual = all(stats1 == stats2)
        expected = False
        self.assertIs(actual, expected)
        stats1.a = 99
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

    @unittest.skip("Marked for deletion.")
    def test_lt(self):
        """
        Tests that a Stats object of booleans is returned.
        """
        expected_stats = self.FunctionalStats(
            **{
                "a": False,
                "b": True,
                "c": False,
                "d": True,
                "e": False,
                "f": True,
                "g": None,
            }
        )
        self.statdict2["g"] = self.statdict1["g"]
        stats1 = self.FunctionalStats(**self.statdict1)
        stats2 = self.FunctionalStats(**self.statdict2)
        actual_stats = stats1.__lt__(stats2)
        for attrname in ("a", "b", "c", "d", "e", "f", "g"):
            actual = getattr(actual_stats, attrname)
            expected = getattr(expected_stats, attrname)
            self.assertIs(actual, expected)

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

    @unittest.skip("No longer being implemented")
    def test_lt__different_classes(self):
        """
        Asserts that lt method fails if operands are of different Stats
        classes, and even if the STAT_LIST for both are identical.
        """
        # copy-paste to lt
        stats1 = self.FunctionalStats(**self.statdict1)
        stats2 = self.FunctionalStats2(**self.statdict2)
        self.assertTupleEqual(stats1.STAT_LIST(), stats2.STAT_LIST())
        with self.assertRaises(TypeError):
            stats1.__lt__(stats2)
        with self.assertRaises(TypeError):
            stats2.__lt__(stats1)

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
        actual = set(self.stats_class.get_stat_dict(0))
        expected = set(self.stats_class.STAT_LIST())
        self.assertSetEqual(actual, expected)

    def test_get_stat_dict(self):
        """
        Tests that key-set in stat-dict is identical to stats listed.
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
        with self.assertRaises(AttributeError) as type_err:
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

    def test_str(self):
        """
        """
        kwargs = self.init_kwargs
        stats = self.stats_class(**kwargs)
        actual = stats.__str__()
        logger.debug("actual: %s", actual)

    def test_add__type_error(self):
        """
        """
        kwargs = self.init_kwargs
        stats1 = self.FunctionalStats(**kwargs)
        stats2 = self.FunctionalStats2(**kwargs)
        with self.assertRaises(TypeError):
            stats1 + stats2

    def test_sub__type_error(self):
        """
        """
        kwargs = self.init_kwargs
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

class AbstractStatsTests(unittest.TestCase):
    """
    Demo of how 'STAT_LIST' should be implemented to be a valid subclass of
    AbstractStats.
    """

    def setUp(self):
        """
        """
        logger.critical("%s", self.id())

    class NoStatListStats(AbstractStats):
        """
        Where 'STAT_LIST' class method is not implemented.
        """

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
            """
            return ()

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
            """
            return ()

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
            """
            return ()

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
        logger.debug(
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
        with self.assertRaises(NotImplementedError) as assert_err:
            self.NonTupleStats()

    def test_cannot_initialize(self):
        """
        Asserts that subclasses that have not implemented the 'STAT_LIST' class
        method cannot be used to create an object.
        """
        with self.assertRaises(TypeError) as type_err:
            self.NoStatListStats()

