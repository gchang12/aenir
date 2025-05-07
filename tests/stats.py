"""
"""

import unittest

from aenir.stats import (
    AbstractStats,
    GenealogyStats,
)

class AbstractStats(unittest.TestCase):
    """
    """

    @unittest.skip("TypeError is not being raised -- Why?")
    def test_cannot_initialize(self):
        """
        """
        with self.assertRaises(TypeError) as type_err:
            stats = AbstractStats()

class GenealogyStatsTests(unittest.TestCase):
    """
    """

    def setUp(self):
        """
        """
        self.init_kwargs = {
            "HP": 0,
            "Str": 0,
            "Mag": 0,
            "Skl": 0,
            "Spd": 0,
            "Lck": 0,
            "Def": 0,
            "Res": 0,
        }

    def test_get_stat_dict__eq_stat_list(self):
        """
        Tests that key-set in stat-dict is identical to STAT_LIST.
        """
        actual = set(GenealogyStats.get_stat_dict(0))
        expected = set(GenealogyStats.STAT_LIST())
        self.assertSetEqual(actual, expected)

    def test_get_stat_dict(self):
        """
        Tests that key-set in stat-dict is identical to stats listed in setUp.
        """
        actual = set(GenealogyStats.get_stat_dict(0))
        expected = set(self.init_kwargs)
        self.assertSetEqual(actual, expected)

    def test_init__missing_kwarg(self):
        """
        """
        kwargs = self.init_kwargs
        hp = kwargs.pop('HP')
        with self.assertRaises(TypeError) as type_err:
            GenealogyStats(**kwargs)

    def test_init__unexpected_kwarg(self):
        """
        """
        with self.assertLogs(logging.WARNING) as log_err:
            assert log_err.warns
