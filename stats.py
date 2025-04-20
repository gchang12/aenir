"""
"""

import abc

class AbstractStats(abc.ABC):
    """
    """
    #STAT_LIST = None

    @classmethod
    @abc.abstractmethod
    def STAT_LIST(self):
        """
        """

    def __init__(self, stat_dict):
        for stat in self.STAT_LIST():
            setattr(self, stat, stat_dict.pop(stat))

    @classmethod
    def __lt__(cls, self, other):
        """
        """
        stat_dict = {}
        for stat in cls.STAT_LIST():
            self_stat = getattr(self, stat)
            other_stat = getattr(other, stat)
            stat_dict[stat] = self_stat < other_stat
        return cls(**stat_dict)

    def __iadd__(self, other):
        """
        """
        for stat in self.STAT_LIST():
            other_stat = getattr(other, stat)
            setattr(self, stat, other_stat)

    def min(self, other):
        """
        """
        for stat in self.STAT_LIST():
            self_stat = getattr(self, stat)
            other_stat = getattr(other, stat)
            setattr(self, stat, min(self_stat, other_stat))

    def max(self, other):
        """
        """
        for stat in self.STAT_LIST():
            self_stat = getattr(self, stat)
            other_stat = getattr(other, stat)
            setattr(self, stat, max(self_stat, other_stat))

    def __repr__(self):
        """
        """
        stat_dict = []
        for stat in self.STAT_LIST():
            stat_dict.append((stat, getattr(self, stat))
        return str(stat_dict)

class GenealogyStats(AbstractStats):

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
            "Str",
            "Mag",
            "Skl",
            "Spd",
            "Lck",
            "Def",
            "Con",
            "Mov",
        )

