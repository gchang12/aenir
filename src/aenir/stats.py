"""
"""

import abc

from aenir.logging import logger


class AbstractStats(abc.ABC):
    """
    Defines methods for comparison, setting, and incrementation of numerical stats.
    """

    @classmethod
    @abc.abstractmethod
    def STAT_LIST(self):
        """
        The kernel of the class; differs for each subclass.
        """

    @classmethod
    def get_stat_dict(cls, fill_value):
        """
        Returns `kwargs` for initialization; each key mapped to `fill_value`.
        """
        #stat_dict = dict( map(lambda stat: (fill_value), cls.STAT_LIST()))
        stat_dict = dict((stat, fill_value) for stat in cls.STAT_LIST())
        #for stat in cls.STAT_LIST():
            #stat_dict[stat] = fill_value
        return stat_dict

    def __init__(self, **stat_dict):
        """
        Alerts user of which stats want declaration if `stat_dict` is incomplete.
        Warns user about unused kwargs.
        """
        # check if statlist in statdict
        if not isinstance(self.STAT_LIST(), tuple):
            raise NotImplementedError("`STAT_LIST` must return a tuple; instead it returns a %r", type(self.STAT_LIST()))
        expected_stats = set(self.STAT_LIST())
        actual_stats = set(stat_dict)
        if not expected_stats.issubset(actual_stats):
            # get list of missing keywords and report to user
            statlist = self.STAT_LIST()
            def by_statlist_ordering(stat):
                """
                Returns position of `stat` in `cls.STAT_LIST()`.
                """
                return statlist.index(stat)
            missing_stats = sorted(
                expected_stats - actual_stats,
                key=by_statlist_ordering,
            )
            raise AttributeError("Please supply values for the following stats: %s" % missing_stats)
        # initialize
        for stat in self.STAT_LIST():
            stat_value = stat_dict.pop(stat)
            setattr(self, stat, stat_value)
        # warn user of unused kwargs
        if stat_dict:
            logger.warning("These keyword arguments have gone unused: %s", stat_dict)

    def imin(self, other):
        """
        Sets each stat in `self` to minimum of itself and corresponding stat in `other`.
        """
        #try:
        if not type(self) == type(other):
            raise TypeError("")
        #except AssertionError as assert_err:
            #raise NotImplementedError
        for stat in self.STAT_LIST():
            self_stat = getattr(self, stat)
            other_stat = getattr(other, stat)
            setattr(self, stat, min(self_stat, other_stat))

    def imax(self, other):
        """
        Sets each stat in `self` to maximum of itself and corresponding stat in `other`.
        """
        #try:
        #assert type(self) == type(other)
        if not type(self) == type(other):
            raise TypeError("")
        #except AssertionError as assert_err:
            #raise NotImplementedError
        for stat in self.STAT_LIST():
            self_stat = getattr(self, stat)
            other_stat = getattr(other, stat)
            setattr(self, stat, max(self_stat, other_stat))

    def iadd(self, other):
        """
        Increments values of `self` by corresponding values in `other`.
        """
        #try:
        #assert type(self) == type(other)
        if not type(self) == type(other):
            raise TypeError("")
        #except AssertionError as assert_err:
            #raise NotImplementedError
        for stat in self.STAT_LIST():
            self_stat = getattr(self, stat)
            other_stat = getattr(other, stat)
            new_stat = self_stat + other_stat
            setattr(self, stat, new_stat)

    def lt(self, other):
        """
        Returns *Stats<bool> indicating which stats in `self` < `other`.
        """
        #try:
        #assert isinstance(self, cls)
        #assert isinstance(other, cls)
        #assert type(self) == type(other)
        if not type(self) == type(other):
            raise TypeError("")
        stat_dict = {}
        #except AssertionError as assert_err:
            #raise NotImplementedError
        for stat in self.STAT_LIST():
            self_stat = getattr(self, stat)
            other_stat = getattr(other, stat)
            stat_dict[stat] = self_stat < other_stat
        return self.__class__(**stat_dict)

    def __repr__(self):
        """
        """
        raise NotImplementedError("Yet to decide on how to display stats.")
        stat_dict = []
        for stat in self.STAT_LIST():
            self_stat = getattr(self, stat)
            stat_dict.append((stat, self_stat))
        return str(stat_dict)

class GenealogyStats(AbstractStats):
    """
    """

    @classmethod
    def STAT_LIST(cls):
        """
        """
        # constant
        return (
            "HP",
            "Str",
            "Mag",
            "Skl",
            "Spd",
            "Lck",
            "Def",
            "Res",
        )


class ThraciaStats(AbstractStats):
    """
    """

    @classmethod
    def STAT_LIST(cls):
        """
        """
        # constant
        return (
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


class GBAStats(AbstractStats):
    """
    """

    @classmethod
    def STAT_LIST(cls):
        """
        """
        # constant
        return (
            "HP",
            "Pow",
            "Skl",
            "Spd",
            "Lck",
            "Def",
            "Con",
            "Mov",
        )

