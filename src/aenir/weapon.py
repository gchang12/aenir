"""
"""

import abc
import sqlite3
from enum import StrEnum 

from aenir.logging import logger

class AbstractWeapon(abc.ABC):
    """
    """
    path_to_db = None

    @abc.abstractmethod
    @staticmethod
    def WEAPON_TYPES():
        """
        """
        return ()

    @abc.abstractmethod
    @staticmethod
    def WEAPON_RANKS():
        """
        """
        return ()

    @abc.abstractmethod
    @staticmethod
    def WEAPON_STATS():
        """
        """
        return ()

    def __init__(self, name, wtype, wrank, wstats):
        """
        """
        # validation
        if wtype in self.WEAPON_TYPES():
            self.type = wtype
        else:
            raise KeyError(f"{wtype} is not a valid weapon type. Valid weapon types: {self.WEAPON_TYPES()}")
        if wrank in self.WEAPON_RANKS():
            self.rank = wrank
        else:
            raise KeyError(f"{wrank} is not a valid weapon rank. Valid weapon ranks: {self.WEAPON_RANKS()}")
        # scan for missing stats
        missing_stats = []
        for wstat in self.WEAPON_STATS():
            try:
                wstat_val = wstats.pop(wstat)
                setattr(self, wstat, wstat_val)
            except KeyError as key_err:
                missing_stats.append(wstat)
        if missing_stats:
            raise AttributeError(f"Missing values for these weapon stats: {missing_stats}")
        self.name = name

    @classmethod
    def query_armory(cls, fields, types, ranks, stats):
        """
        """
        stmt = ""
        path_to_db = self.path_to_db
        with sqlite3.connect(path_to_db) as cnxn:
            pass
        raise NotImplementedError

