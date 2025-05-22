"""
"""

import abc
import sqlite3
import json
from typing import Tuple

from aenir.games import FireEmblemGame
from aenir.stats import (
    GenealogyStats,
    GBAStats,
    ThraciaStats,
    AbstractStats,
)
from aenir.logging import logger

class BaseMorph(abc.ABC):
    """
    """

    @classmethod
    @abc.abstractmethod
    def GAME(cls):
        """
        """
        # should return instance of FireEmblemGame
        raise NotImplementedError

    @classmethod
    def STATS(cls):
        """
        """
        return {
            4: GenealogyStats,
            5: ThraciaStats,
            6: GBAStats,
            7: GBAStats,
            8: GBAStats,
            9: GenealogyStats,
        }[cls.GAME().value]

    @classmethod
    def path_to(cls, file: str):
        """
        """
        return "/".join(("static", cls.GAME().url_name, file))

    @staticmethod
    def query_db(
            path_to_db: str,
            table: str,
            fields: Tuple[str],
            filters: dict[str, str],
        ):
        """
        """
        query = f"SELECT {', '.join(fields)} FROM {table}"
        if filters is not None:
            conditions = ", ".join(
                [
                    (f"{field}='{value}'") for field, value in filters.items()
                ]
            )
            query += " WHERE " + conditions
        query += ";"
        with sqlite3.connect(path_to_db) as cnxn:
            cnxn.row_factory = sqlite3.Row
            return cnxn.execute(query)

    def __init__(self):
        """
        """
        self.Stats = self.STATS()

    def lookup(
            self,
            home_data: Tuple[str, str],
            target_data: Tuple[str, str],
            tableindex: int,
        ):
        """
        """
        # unpack arguments
        home_table, value_to_lookup = home_data
        target_table, field_to_scan = target_data
        logger.debug(
            "Checking if '%s' from %s[index] has an equivalent in %s[%s].",
            value_to_lookup, home_table, target_table, field_to_scan,
        )
        path_to_json = self.path_to(f"{home_table}-JOIN-{target_table}.json")
        logger.debug(
            "Checking if '%s' exists in the dict in '%s'",
            value_to_lookup, path_to_json,
        )
        with open(path_to_json, encoding='utf-8') as rfile:
            aliased_value = json.load(rfile).pop(value_to_lookup)
        logger.debug(
            "'%s' from %s[index] exists as %r in %s[%s]",
            value_to_lookup, home_table, aliased_value, target_table, field_to_scan,
        )
        if aliased_value is None:
            query_kwargs = None
        else:
            table = "%s%d" % (target_table, tableindex)
            filters = {field_to_scan: aliased_value}
            path_to_db = self.path_to("cleaned_stats.db")
            fields = self.Stats.STAT_LIST()
            logger.debug(
                "BaseMorph.lookup(self, %r, %r, %r, %r)",
                path_to_db,
                table,
                fields,
                filters,
            )
            query_kwargs = {
                "path_to_db": path_to_db,
                "table": table,
                "fields": fields,
                "filters": filters,
            }
        return query_kwargs

class Morph(BaseMorph):
    """
    """
    # NOTE: game_no to be set in each subclass of this class.
    game_no = None

    @classmethod
    @abc.abstractmethod
    def GAME(cls):
        """
        """
        #if cls.__name__ == "Morph":
            # TODO: Figure out what specifically to warn the user about.
            #logger.warning("Instantiating Morph class; some features will be unavailable. Please use appropriate subclass of Morph for full functionality.")
        return FireEmblemGame(cls.game_no)

    @classmethod
    def CHARACTER_LIST(cls):
        """
        """
        filename = "characters__base_stats-JOIN-characters__growth_rates.json"
        path_to_json = cls.path_to(filename)
        with open(path_to_json, encoding='utf-8') as rfile:
            character_list = list(json.load(rfile))
        return character_list

    def __init__(self, name: str, *, which_bases: int, which_growths: int):
        super().__init__()
        self.game = self.GAME()
        character_list = self.CHARACTER_LIST()
        if name not in character_list:
            raise ValueError(
                "'%s' not found. List of Fire Emblem: %r characters: %r" \
                % (name, self.game.formal_name, character_list)
            )
        self.name = name
        # class and level
        path_to_db = self.path_to("cleaned_stats.db")
        table = "characters__base_stats%d" % which_bases
        fields = self.Stats.STAT_LIST() + ("Class", "Lv")
        filters = {"Name": name}
        basestats_query = self.query_db(
            path_to_db,
            table,
            fields,
            filters,
        ).fetchall()
        stat_dict = dict(basestats_query.pop())
        self.current_cls = stat_dict.pop("Class")
        self.current_lv = stat_dict.pop("Lv")
        # bases
        self.current_stats = self.Stats(**stat_dict)
        # growths
        resultset = self.query_db(
            **self.lookup(
                ("characters__base_stats", name),
                ("characters__growth_rates", "Name"),
                which_growths,
            )
        ).fetchall()
        self.growth_rates = self.Stats(**resultset.pop(which_growths))
        # maximum
        self.current_clstype = "characters__base_stats"
        maxes_resultset = self.query_db(
            **self.lookup(
                (self.current_clstype, name),
                ("classes__maximum_stats", "Class"),
                tableindex=0,
            )
        ).fetchall()
        self.max_stats = self.Stats(**maxes_resultset.pop())
        # (miscellany)
        self._meta = {'History': []}
        if name.replace(" (HM)", "") + " (HM)" in character_list:
            self._meta['Hard Mode'] = " (HM)" in name
        self.max_level = None
        self.min_promo_level = None
        self.promo_cls = None

    def _set_max_level(self):
        """
        """
        # exceptions:
        # FE4: 30 for promoted, 20 for unpromoted
        # FE8: unpromoted trainees are capped at 10
        self.max_level = 20

    def _set_min_promo_level(self):
        """
        """
        # exceptions:
        # FE4: 20
        # FE5: for Lara if promo_cls == 'Dancer': 1
        # FE5: Leif, Linoan: 1
        # FE6: Roy: 1
        # FE7: Hector, Eliwood: 1
        self.min_promo_level = 10

    def level_up(self, num_levels: int):
        """
        """
        # get max level
        if self.max_level is None:
            self._set_max_level()
        # stop if user is going to overlevel
        if num_levels + self.current_lv > self.max_level:
            raise ValueError("")
        # ! increase stats
        self.current_stats += self.growth_rates * 0.01 * num_levels
        # ! increase level
        self.current_lv += num_levels
        # cap stats
        self.current_stats.imin(self.max_stats)

    def promote(self):
        """
        """
        # check if unit's level is high enough to enable promotion
        if self.min_promo_level is None:
            self._set_min_promo_level()
        if self.current_lv < self.min_promo_level:
            raise ValueError(f"{self.name} must be at least level {self.min_promo_level} to promote. Current level: {self.current_lv}.")
        # get promotion data
        value_to_lookup = {
            "characters__base_stats": self.name,
            "classes__promotion_gains": self.current_cls,
        }[self.current_clstype]
        query_kwargs = self.lookup(
            (self.current_clstype, value_to_lookup),
            ("classes__promotion_gains", "Class"),
            tableindex=0,
        )
        query_kwargs['fields'] = list(query_kwargs['fields']) + ["Promotion"]
        resultset = self.query_db(**query_kwargs).fetchall()
        # quit if resultset is empty
        if not resultset:
            raise ValueError(f"{self.name} has no available promotions.")
        # if resultset has length > 1, filter to relevant
        elif len(resultset) > 1:
            resultset = list(
                filter(
                    lambda result: result['Promotion'] == self.promo_cls,
                    resultset,
                )
            )
        # ** PROMOTION START! **
        # record history
        self._meta["History"].append((self.current_lv, self.current_cls))
        # initialize stat_dict, then set attributes
        stat_dict = dict(resultset.pop())
        # set 'current_clstype' for future queries
        self.current_clstype = "classes__promotion_gains"
        # ! change class
        self.current_cls = stat_dict.pop('Promotion')
        # ! increment stats
        promo_bonuses = self.Stats(**stat_dict)
        self.current_stats += promo_bonuses
        # ! set max stats, then cap current stats
        query_kwargs2 = self.lookup(
            (self.current_clstype, self.current_cls),
            ("classes__maximum_stats", "Class"),
            tableindex=0,
        )
        stat_dict2 = self.query_db(**query_kwargs2).fetchall()
        self.max_stats = self.Stats(**stat_dict2.pop())
        self.current_stats.imin(self.max_stats)
        # ! reset level
        self.current_lv = 1
        # set promotion class to None
        self.promo_cls = None

    # TODO: Flesh out informational methods

    def is_maxed(self):
        """
        """
        # What if the difference is trivial but nonzero?
        # - iadd dunder has been amended s.t. exact matches are guaranteed every time.
        raise NotImplementedError
        return self.current_stats == self.max_stats

    def __lt__(self, other):
        """
        """
        raise NotImplementedError
        if not type(self) == type(other):
            raise TypeError("")
        comparison = self.current_stats < other.current_stats
        # put in data from _meta here... somehow

