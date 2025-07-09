"""
Declares classes that store numerical stat data for a given unit.
"""

import abc

from aenir._logging import logger


class AbstractStats(abc.ABC):
    """
    Defines methods for comparison, setting, and incrementation of numerical stats.
    """

    @staticmethod
    @abc.abstractmethod
    def STAT_LIST():
        """
        A kernel of the class; expects a tuple of the names of all stats.
        """
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def ZERO_GROWTH_STAT_LIST():
        """
        A kernel of the class; expects a tuple of the names of stats that have zero growth rates.
        """
        raise NotImplementedError

    @classmethod
    def get_stat_dict(cls, fill_value):
        """
        Returns `kwargs` for initialization; each key is mapped to `fill_value`.
        """
        stat_dict = dict((stat, fill_value) for stat in cls.STAT_LIST())
        return stat_dict

    @classmethod
    def get_growable_stats(cls):
        """
        Returns iterable of stats with growth rates.
        """
        return filter(lambda stat_: stat_ not in cls.ZERO_GROWTH_STAT_LIST(), cls.STAT_LIST())

    def as_dict(self):
        """
        Returns key-val pairs of stats as dict object.
        """
        stat_dict = {stat: getattr(self, stat) for stat in self.STAT_LIST()}
        return stat_dict

    def as_list(self):
        """
        Returns key-val pairs of stats as list of 2-tuples.
        """
        stat_list = [(stat, getattr(self, stat)) for stat in self.STAT_LIST()]
        return stat_list

    def copy(self):
        """
        Returns new instance of Stats identical to this one.
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
        statlist = self.STAT_LIST()
        if not isinstance(statlist, tuple):
            raise NotImplementedError("`STAT_LIST` must return a tuple; instead it returns a %r", type(statlist))
        expected_stats = set(statlist)
        actual_stats = set(stat_dict)
        if not expected_stats.issubset(actual_stats):
            # get list of missing keywords and report to user
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
        for stat in statlist:
            stat_value = stat_dict[stat]
            setattr(self, stat, stat_value)
        # warn user of unused kwargs
        unused_stats = set(stat_dict) - set(statlist)
        if unused_stats:
            logger.warning("These keyword arguments have gone unused: %s", unused_stats)

    def __mul__(self, other):
        """
        Reads current stats, multiplies each stat by a scalar, then returns the result in a new Stats object.
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
        Adds two Stats objects like they're Euclidean vectors and returns the result in a new Stats object.
        Error is thrown if the Stats objects are not of the same type.
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
        Obtains difference of growable stats of two Stats objects and returns the result in a new Stats object.
        Error is thrown if the Stats objects are not of the same type.
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
        Returns a Stats object stating which attributes are equal and which are unequal.
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
        Returns iterable of growable stats.
        """
        for stat in self.get_growable_stats():
            yield getattr(self, stat)

    def __repr__(self, with_title=True):
        """
        Returns pretty-printed str-list of stats.
        """
        statlist = self.as_list()
        #format_str = "% 4s: %5.2s"
        def get_formatted_statlist(statval):
            """
            """
            format_str = "% 4s: %5.2f"
            field, value = statval
            value = value or 0
            return format_str % (field, value)
        statlist_as_str = "\n".join(get_formatted_statlist(statval) for statval in statlist)
        if with_title:
            header = self.__class__.__name__
            header_border = len(header) * "="
            statlist_as_str = "\n".join([header, header_border, statlist_as_str])
        return statlist_as_str

    def __str__(self):
        """
        Returns pretty-printed str-list of stats.
        """
        return self.__repr__()

class GenealogyStats(AbstractStats):
    """
    Declares stats used for FE4: Genealogy of the Holy War.
    """

    @staticmethod
    def STAT_LIST():
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

    @staticmethod
    def ZERO_GROWTH_STAT_LIST():
        return ()

class ThraciaStats(AbstractStats):
    """
    Declares stats used for FE5: Thracia 776.
    """

    @staticmethod
    def STAT_LIST():
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

    @staticmethod
    def ZERO_GROWTH_STAT_LIST():
        return (
            "Lead",
            "MS",
            "PC",
        )


class GBAStats(AbstractStats):
    """
    Declares stats used for FE6, FE7, and FE8.
    """

    @staticmethod
    def STAT_LIST():
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

    @staticmethod
    def ZERO_GROWTH_STAT_LIST():
        return (
            "Con",
            "Mov",
        )


class RadiantStats(AbstractStats):
    """
    Declares stats used for FE9.
    """

    @staticmethod
    def STAT_LIST():
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

    @staticmethod
    def ZERO_GROWTH_STAT_LIST():
        # constant
        return (
            "Mov",
            "Con",
            "Wt",
        )

