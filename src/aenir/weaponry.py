"""
"""

import abc
import sqlite3
from enum import StrEnum 

# hook equipment ranks up later
#from aenir.games import FireEmblemGame
#game, unit

from aenir.logging import logger

class AbstractWeaponry(abc.ABC):
    """
    """
    path_to_db = None

    @abc.abstractmethod
    @staticmethod
    def WEAPON_TYPES(cls):
        """
        """
        return ()

    @abc.abstractmethod
    @staticmethod
    def WEAPON_RANKS(cls):
        """
        """
        return ()

    @abc.abstractmethod
    @staticmethod
    def WEAPON_STATS(cls):
        """
        """
        return ()

    # TODO: Decide how to implement this kernel
    @abc.abstractmethod
    #@classmethod
    @staticmethod
    def _WeaponType():
        """
        """
        class WeaponType(StrEnum):
            """
            """
        return WeaponType

    # TODO: Decide how to implement this kernel
    @abc.abstractmethod
    #@classmethod
    @staticmethod
    def _WeaponRank():
        """
        """
        class WeaponRank(StrEnum):
            """
            """
        return WeaponRank

    # TODO: Decide how to implement this kernel
    @abc.abstractmethod
    #@classmethod
    @staticmethod
    def WEAPON_STATS():
        """
        """
        return ()

    #@abc.abstractmethod
    #@classmethod
    class Weapon:
        """
        """
        Rank = _WeaponRank()
        Type = _WeaponType()
        Stats = _WeaponStats()

        def __init__(self, name, rank, type_, **stats):
            """
            """
            self.name = name
            self.rank = self.Rank(rank)
            self.type = self.Type(type_)
            stats_ = {}
            missing_stats = []
            for weapon_stat in WEAPON_STATS():
                try:
                    stat = stats.pop(weapon_stat)
                except KeyError:
                    missing_stats.append(weapon_stat)
                stats_[weapon_stat] = stat
            if missing_stats:
                raise AttributeError
            # other data goes here.
            # TODO: Should I not cut this all up?

    def __init__(self, weapon_ranks):
        """
        """
        WeaponRank = self.Weapon.Rank
        WeaponType = self.Weapon.Type
        _weapon_ranks = {}
        for weapon_type, max_rank in weapon_ranks.items():
            true_weapon_type = WeaponType(weapon_type)
            if max_rank is not None:
                true_max_rank = WeaponRank(max_rank)
            else:
                true_max_rank = None
            _weapon_ranks[true_weapon_type] = true_max_rank
            # else set to None
        self.weapon_ranks = _weapon_ranks

    # TODO: query by: rank, type, etc.
    @classmethod
    def query_for_all_weapons(cls):
        """
        """
        stmt = ""
        path_to_db = self.path_to_db
        with sqlite3.connect(path_to_db) as cnxn:
            pass

    def query_for_usable_weapons(self):
        """
        """
        stmt = ""
        path_to_db = self.path_to_db
        with sqlite3.connect(path_to_db) as cnxn:
            pass

    def can_use(self, weapon) -> bool:
        """
        """
        return 

