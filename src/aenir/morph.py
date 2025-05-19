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
            fields: tuple[str],
            filters: dict[str, str],
        ):
        """
        """
        query = f"SELECT {', '.join(fields)} FROM {table}"
        if filters:
            conditions = ", ".join(
                [
                    (str(field) + "='" + str(value) + "'")
                    for field, value in filters.items()
                ]
            )
            query += " WHERE " + conditions
        query += ";"
        with sqlite3.connect(path_to_db) as cnxn:
            cnxn.row_factory = sqlite3.Row
            return cnxn.execute(query)

    def lookup(
            self,
            ltable_args: Tuple[str, str],
            rtable_args: Tuple[str, str],
            tableindex: int
        ):
        """
        """
        logger.info("BaseMorph.set_targetstats(self, %s, %s)", ltable_args, rtable_args)
        # unpack arguments
        ltable, lindex_val = ltable_args
        rtable, to_col = rtable_args
        path_to_json = self.path_to(f"{ltable}-JOIN-{rtable}.json")
        with open(path_to_json, encoding='utf-8') as rfile:
            from_col = json.load(rfile).pop(lindex_val)
        if from_col is None:
            resultset = None
        else:
            table = rtable + str(tableindex)
            index_key = {to_col: from_col}
            resultset = self.get_stats(
                table,
                index_key,
            )
        return resultset

class Morph(BaseMorph):
    """
    """
    game_no = None

    @classmethod
    def GAME(cls):
        """
        """
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
        game = self.GAME()
        self.game_no = game.value
        self.Stats = self.STATS()
        self.unit = unit
        # class and level
        path_to_db = self.path_to("cleaned_stats.db")
        table = "characters__base_stats0"
        fields = game.STAT_LIST() + ("Class", "Lv")
        filters = {"Name": unit}
        stat_dict = self.query_db(
            path_to_db,
            table,
            fields,
            filters,
        ).fetchone()
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
        self.growth_rates = resultset.pop()
        # maximum
        self.current_clstype = "characters__base_stats"
        self.lookup(
            (self.current_clstype, unit),
            ("classes__maximum_stats", "Class"),
            tableindex=0,
        )
        self.max_stats = resultset.pop()
        # (miscellany)
        self.history = []
        self.comparison_labels = {}
        if unit.replace(" (HM", "") + " (HM)" in self.CHARACTER_LIST():
            self.comparison_labels['Hard Mode'] = " (HM)" in unit

