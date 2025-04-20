"""
"""

import abc

class AbstractStats(abc.ABC):
    """
    """
    #STAT_LIST = None

    @abc.abstractmethod
    def STAT_LIST(self):
        """
        """
        return ()

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

class GenealogyStats(AbstractStats):

    def STAT_LIST(self):
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

    def __init__(self, HP, Str, Mag, Skl, Spd, Lck, Def, Res):
        """
        """
        self.HP = HP
        self.Str = Str
        self.Mag = Mag
        self.Skl = Skl
        self.Spd = Spd
        self.Lck = Lck
        self.Def = Def
        self.Res = Res


class ThraciaStats(AbstractStats):
    """
    """

    def STAT_LIST(self):
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

    def __init__(self, HP, Str, Mag, Skl, Spd, Lck, Def, Con, Mov):
        """
        """
        self.HP = HP
        self.Str = Str
        self.Mag = Mag
        self.Skl = Skl
        self.Spd = Spd
        self.Lck = Lck
        self.Def = Def
        self.Con = Con
        self.Mov = Mov


class GBAStats(AbstractStats):
    """
    """

    def STAT_LIST(self):
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

    def __init__(self, HP, Pow, Skl, Spd, Lck, Def, Res):
        """
        """
        # stat attributes have private access
        self.HP = HP
        self.Pow = Pow
        self.Skl = Skl
        self.Spd = Spd
        self.Lck = Lck
        self.Def = Def
        self.Res = Res

