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
    def STAT_LIST(cls):
        """
        A kernel of the class; expects a tuple of the names of all stats.
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def ZERO_GROWTH_STAT_LIST(cls):
        """
        A kernel of the class; expects a tuple of the names of stats that have zero growth rates.
        """
        raise NotImplementedError

    @classmethod
    def get_stat_dict(cls, fill_value):
        """
        Returns `kwargs` for initialization; each key mapped to `fill_value`.
        """
        stat_dict = dict((stat, fill_value) for stat in cls.STAT_LIST())
        return stat_dict

    @classmethod
    def get_growable_stats(cls):
        """
        """
        return filter(lambda stat_: stat_ not in cls.ZERO_GROWTH_STAT_LIST(), cls.STAT_LIST())

    def as_dict(self):
        """
        """
        stat_dict = {stat: getattr(self, stat) for stat in self.STAT_LIST()}
        return stat_dict

    def as_list(self):
        """
        """
        stat_list = [(stat, getattr(self, stat)) for stat in self.STAT_LIST()]
        return stat_list

    def copy(self):
        """
        """
        stat_dict = {}
        for stat in self.STAT_LIST():
            stat_dict[stat] = getattr(self, stat)
        return self.__class__(**stat_dict)

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
            stat_value = stat_dict[stat]
            setattr(self, stat, stat_value)
        # warn user of unused kwargs
        if stat_dict:
            logger.warning("These keyword arguments have gone unused: %s", stat_dict)

    def __mul__(self, other):
        """
        """
        stat_dict = {}
        for stat in self.STAT_LIST():
            self_stat = getattr(self, stat)
            stat_dict[stat] = round(self_stat * other, 2)
        return self.__class__(**stat_dict)

    def imin(self, other):
        """
        Sets each stat in `self` to minimum of itself and corresponding stat in `other`.
        """
        if not type(self) == type(other):
            raise TypeError("Stats must be of the same type: %r != %r", (type(self) % type(other)))
        for stat in self.STAT_LIST():
            self_stat = getattr(self, stat)
            other_stat = getattr(other, stat)
            setattr(self, stat, min(self_stat, other_stat))

    def imax(self, other):
        """
        Sets each stat in `self` to maximum of itself and corresponding stat in `other`.
        """
        if not type(self) == type(other):
            raise TypeError("Stats must be of the same type: %r != %r", (type(self) % type(other)))
        for stat in self.STAT_LIST():
            self_stat = getattr(self, stat)
            other_stat = getattr(other, stat)
            setattr(self, stat, max(self_stat, other_stat))

    def __iadd__(self, other):
        """
        Increments values of `self` by corresponding values in `other`.
        """
        if not type(self) == type(other):
            raise TypeError("Stats must be of the same type: %r != %r", (type(self) % type(other)))
        for stat in self.STAT_LIST():
            self_stat = getattr(self, stat)
            other_stat = getattr(other, stat)
            new_stat = round(self_stat + other_stat, 2)
            setattr(self, stat, new_stat)
        return self

    def __add__(self, other):
        """
        """
        if not type(self) == type(other):
            raise TypeError("Stats must be of the same type: %r != %r", (type(self) % type(other)))
        stat_dict = {}
        for stat in self.STAT_LIST():
            #for stat in self.STAT_LIST():
            self_stat = getattr(self, stat)
            other_stat = getattr(other, stat)
            stat_dict[stat] = round(self_stat + other_stat, 2)
        return self.__class__(**stat_dict)

    def __sub__(self, other):
        """
        """
        if not type(self) == type(other):
            raise TypeError("Stats must be of the same type: %r != %r", (type(self) % type(other)))
        stat_dict = {}
        for stat in self.get_growable_stats():
            #for stat in self.STAT_LIST():
            self_stat = getattr(self, stat)
            other_stat = getattr(other, stat)
            stat_dict[stat] = round(self_stat - other_stat, 2)
        for stat in self.ZERO_GROWTH_STAT_LIST():
            stat_dict[stat] = None
        return self.__class__(**stat_dict)

    def __eq__(self, other):
        """
        """
        if not type(self) == type(other):
            raise TypeError("Stats must be of the same type: %r != %r", (type(self) % type(other)))
        #for stat in filter(lambda stat_: stat not in self.ZERO_GROWTH_STAT_LIST(), self.STAT_LIST()):
        stat_dict = {}
        for stat in self.STAT_LIST():
            #for stat in filter(lambda stat_: stat not in self.ZERO_GROWTH_STAT_LIST(), self.STAT_LIST()):
            #for stat in self.STAT_LIST():
            self_stat = getattr(self, stat)
            other_stat = getattr(other, stat)
            stat_dict[stat] = self_stat == other_stat
        return self.__class__(**stat_dict)

    def __iter__(self):
        """
        """
        for stat in self.get_growable_stats():
            yield getattr(self, stat)

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

    @classmethod
    def ZERO_GROWTH_STAT_LIST(cls):
        """
        """
        return (
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
            "Lead",
            "MS",
            "PC",
        )

    @classmethod
    def ZERO_GROWTH_STAT_LIST(cls):
        """
        """
        return (
            "Lead",
            "MS",
            "PC",
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
            "Res",
            "Con",
            "Mov",
        )

    @classmethod
    def ZERO_GROWTH_STAT_LIST(cls):
        """
        """
        return (
            "Con",
            "Mov",
        )


class RadiantStats(AbstractStats):
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
            "Mov",
            "Con",
            "Wt",
        )

    @classmethod
    def ZERO_GROWTH_STAT_LIST(cls):
        """
        """
        # constant
        return (
            "Mov",
            "Con",
            "Wt",
        )

