"""
"""

import abc
import enum
import sqlite3

# hook equipment ranks up later
#from aenir.games import FireEmblemGame
#game, unit

from aenir.logging import logger

class AbstractWeaponry(abc.ABC):
    """
    """
    path_to_db = None

    @abc.abstractmethod
    @classmethod
    def Weapon(cls):
        """
        """

        class Type:
            """
            """
            # should return an enum class
            raise NotImplementedError

        class Rank:
            """
            """
            # should return an enum class
            raise NotImplementedError

        # should return a class
        raise NotImplementedError

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

