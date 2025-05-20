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
        self.game = self.GAME()
        self.Stats = self.STATS()

    def lookup(
            self,
            home_data: Tuple[str, str],
            target_data: Tuple[str, str],
            tableindex: int,
        ):
        """
        """
        logger.info("BaseMorph.lookup(self, %s, %s)", home_data, target_data)
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
            "'%s' from %s[index] exists as '%s' in %s[%s]",
            value_to_lookup, home_table, aliased_value, target_table, field_to_scan,
        )
        if aliased_value is None:
            resultset = None
        else:
            table = target_table + str(tableindex)
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
            resultset = self.query_db(
                path_to_db,
                table,
                fields,
                filters,
            )
        return resultset

class Morph(BaseMorph):
    """
    """
    # NOTE: game_no to be set in each subclass of this class.
    game_no = None

    @classmethod
    def GAME(cls):
        """
        """
        if cls.__name__ == "Morph":
            # TODO: Figure out what to warn the user about.
            logger.warning("")
        return FireEmblemGame(game_no)

    @classmethod
    def CHARACTER_LIST(cls):
        """
        """
        filename = "characters__base_stats-JOIN-characters__growth_rates.json"
        path_to_json = cls.path_to(filename)
        with open(str(json_path), encoding='utf-8') as rfile:
            character_list = list(json.load(rfile))
        return character_list

    def __init__(self, unit: str, *, which_bases: int, which_growths: int):
        super().__init__()
        self.unit = unit
        # class and level
        path_to_db = self.path_to("cleaned_stats.db")
        table = "characters__base_stats0"
        fields = self.Stats.STAT_LIST() + ("Class", "Lv")
        filters = {"Name": unit}
        basestats_query = self.query_db(
            path_to_db,
            table,
            fields,
            filters,
        ).fetchall()
        stat_dict = basestats_query.pop(which_bases)
        self.current_cls = stat_dict.pop("Class")
        self.current_lv = stat_dict.pop("Lv")
        # bases
        self.current_stats = self.Stats(**stat_dict)
        # growths
        resultset = self.lookup(
            ("characters__base_stats", unit),
            ("characters__growth_rates", "Name"),
            which_growths,
        )
        self.growth_rates = resultset.pop(which_growths)
        # maximum
        self.current_clstype = "characters__base_stats"
        maxes_resultset = self.lookup(
            (self.current_clstype, unit),
            ("classes__maximum_stats", "Class"),
            tableindex=0,
        )
        self.max_stats = maxes_resultset.pop()
        # (miscellany)
        self.history = []
        self.comparison_labels = {}
        if unit.replace(" (HM)", "") + " (HM)" in self.CHARACTER_LIST():
            self.comparison_labels['Hard Mode'] = " (HM)" in unit

