#!/usr/bin/python3
"""
Defines the BaseMorph class.

BaseMorph: Defines methods for verifying manual input, and matching it to the proper sources.
"""

import logging
import io
from typing import Tuple, List
import json
from pathlib import Path

import pandas as pd
from aenir.cleaner import SerenesCleaner

class BaseMorph(SerenesCleaner):
    """
    Defines parameters and methods for stat look-up and name verification.

    current_clstype: Determines which table to match from.
    current_cls: Value of the current class, to be matched.
    target_stats: Stores the stats to be retrieved.
    history: Stores the history of a unit as a list of (Class, Lv) tuples.
    """

    def __init__(self, game_num: int, datadir_root: str):
        """
        Extends: SerenesCleaner.__init__(self, game_num)

        Defines: current_clstype, current_cls, target_stats
        """
        SerenesCleaner.__init__(self, game_num)
        # essential to set_targetstats method
        self.target_stats = None
        self.current_stats = None
        # history (class, lv) tuples, and labels for comparison DataFrame
        self.history = []
        self.comparison_labels = {}
        # load tables
        if type(datadir_root) == str:
            self.home_dir = Path(datadir_root).joinpath(self.game_name)
        self.tables_file = "cleaned_stats.db"
        for urlpath in self.page_dict:
            self.load_tables(urlpath)
        
    def verify_clsrecon_file(self, ltable_args: Tuple[str, str, str], rtable_args: Tuple[str, str]):
        """
        Prints: clsrecon_dict.keys not in ltable[lindex_col], clsrecon_dict.values not in rtable[to_col].

        Note: In order for this method to work, logging.level must be set to logging.INFO.
        """
        logging.info("BaseMorph.verify_clsrecon_file(self, %s, %s)", ltable_args, rtable_args)
        # unpack arguments
        ltable_url, lindex_col, from_col = ltable_args
        rtable_url, to_col = rtable_args
        # load clsrecon_dict
        ltable_name = self.page_dict[ltable_url]
        rtable_name = self.page_dict[rtable_url]
        json_path = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        with io.open(str(json_path), encoding='utf-8') as rfile:
            clsrecon_dict = json.load(rfile)
        # compile ltable pkey names
        ltable_nameset = set()
        for table in self.url_to_tables[ltable_url]:
            ltable_nameset.update(set(table.loc[:, lindex_col]))
        # compile rtable values
        rtable_nameset = set()
        for table in self.url_to_tables[rtable_url]:
            rtable_nameset.update(set(table.loc[:, to_col]))
        # check1: clsrecon_dict.keys subset of ltable_nameset
        check1 = set(clsrecon_dict) - ltable_nameset
        logging.info("%d key(s) in '%s', but not in '%s.%s': %s", len(check1), str(json_path), ltable_name, lindex_col, check1)
        # check2: clsrecon_dict.values subset of rtable_nameset
        check2 = set(clsrecon_dict.values()) - {None} - rtable_nameset
        logging.info("%d value(s) in '%s', but not in '%s.%s': %s", len(check2), str(json_path), rtable_name, to_col, check2)

    def verify_maximum_stats(self):
        """
        Prints columns that are in 'classes/maximum-stats' but not in 'characters/base-stats'.

        Note: In order for this method to work, logging.level must be set to logging.INFO.
        """
        logging.info("BaseMorph.verify_maximum_stats(self)")
        bases_name = "characters/base-stats"
        maxes_name = "classes/maximum-stats"
        bases = set(self.url_to_tables[bases_name][0].columns) - {"Name", "Class", "Lv"}
        maxes = set(self.url_to_tables[maxes_name][0].columns) - {"Class"}
        diff = maxes - bases
        logging.info("%d names in '%s' but not in '%s': %s", len(diff), maxes_name, bases_name, diff)

    def set_targetstats(self, ltable_args: Tuple[str, str], rtable_args: Tuple[str, str], tableindex: int):
        """
        Sets BaseMorph.target_stats to the pd.[DataFrame|Series] per clsrecon_dict.

        ltable_url, lindex_col = ltable_args
        rtable_url, to_col = rtable_args
        lindex_col |-(clsrecon_dict)-> from_col === to_col
        """
        logging.info("BaseMorph.set_targetstats(self, %s, %s)", ltable_args, rtable_args)
        # unpack arguments
        ltable_url, lindex_val = ltable_args
        rtable_url, to_col = rtable_args
        # load clsrecon_dict from json
        ltable_name = self.page_dict[ltable_url]
        rtable_name = self.page_dict[rtable_url]
        json_path = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        with open(str(json_path), encoding='utf-8') as rfile:
            clsrecon_dict = json.load(rfile)
        from_col = clsrecon_dict[lindex_val]
        if from_col is None:
            self.target_stats = None
        else:
            self.target_stats = self.url_to_tables[rtable_url][tableindex].set_index(to_col).loc[from_col, :]

    def get_character_list(self) -> List[str]:
        """
        Returns a List[str] of base!character names mapped to growths!character names.

        Raises:
        - FileNotFoundError: not home_dir.joinpath("characters__base_stats-JOIN-characters__growth_rates.json").exists()
        - json.decoder.JSONDecodeError: File is not in JSON form.
        """
        logging.info("BaseMorph.get_character_list(self)")
        ltable_url = "characters/base-stats"
        rtable_url = "characters/growth-rates"
        ltable_name = self.page_dict[ltable_url]
        rtable_name = self.page_dict[rtable_url]
        json_path = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        # query character list from JSON (FileNotFoundError may be raised before that)
        with io.open(str(json_path), encoding='utf-8') as rfile:
            clsrecon_dict = json.load(rfile)
        chrlist = []
        # filter to include non-None entries
        for chrname, growth_equivalent in clsrecon_dict.items():
            if growth_equivalent is None:
                continue
            if chrname in chrlist:
                continue
            chrlist.append(chrname)
        # return keys mapped to non-None
        logging.info("%d names found: %s", len(chrlist), chrlist)
        return chrlist

if __name__ == '__main__':
    pass
