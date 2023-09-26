#!/usr/bin/python3
"""
Defines the BaseMorph class.

BaseMorph: Defines methods for verifying manual input, and matching it to the proper sources.
"""

import logging
import io
from typing import Tuple
import json

from aenir.cleaner import SerenesCleaner

class BaseMorph(SerenesCleaner):
    """
    Defines parameters and methods for stat look-up and name verification.

    current_clstype: Determines which table to match from.
    current_cls: Value of the current class, to be matched.
    target_stats: Stores the stats to be retrieved.
    promo_index: Determines which branch in a promotion the unit will choose.
    """

    def __init__(self, game_num: int):
        """
        Extends: SerenesCleaner.__init__(self, game_num)

        Defines: current_clstype, current_cls, target_stats, promo_index
        """
        SerenesCleaner.__init__(self, game_num)
        logging.info("BaseMorph.__init__(self, %d)", game_num)
        # essential to set_targetstats method
        self.target_stats = None
        self.current_stats = None

    def __repr__(self):
        """
        Uses the __repr__ method for the pd.Series object representing the current_stats.
        """
        return self.current_stats.__repr__()

    def verify_clsrecon_file(self, ltable_args: Tuple[str, str, str], rtable_args: Tuple[str, str]):
        """
        Prints: clsrecon_dict.keys not in ltable[lpkey], clsrecon_dict.values not in rtable[to_col].

        Note: In order for this method to work, logging.level must be set to logging.INFO.
        """
        logging.info("BaseMorph.verify_clsrecon_file(self, %s, %s)", ltable_args, rtable_args)
        # unpack arguments
        ltable_url, lpkey, from_col = ltable_args
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
            ltable_nameset.update(set(table.loc[:, lpkey]))
        # compile rtable values
        rtable_nameset = set()
        for table in self.url_to_tables[rtable_url]:
            rtable_nameset.update(set(table.loc[:, to_col]))
        # check1: clsrecon_dict.keys subset of ltable_nameset
        check1 = set(clsrecon_dict) - ltable_nameset
        logging.info("%d key(s) in '%s', but not in '%s.%s': ", len(check1), str(json_path), ltable_name, lpkey)
        for name in check1:
            logging.info(name)
        # check2: clsrecon_dict.values subset of rtable_nameset
        check2 = set(clsrecon_dict.values()) - {None} - rtable_nameset
        logging.info("%d value(s) in '%s', but not in '%s.%s': ", len(check2), str(json_path), rtable_name, to_col)
        for name in check2:
            logging.info(name)

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
        # check1: bases - maxes
        check1 = bases - maxes
        logging.info("%d names in '%s' but not '%s': ", len(check1), bases_name, maxes_name)
        for name in check1:
            logging.info(name)
        # check2: maxes - bases
        check2 = bases - maxes
        logging.info("%d names in '%s' but not '%s': ", len(check2), maxes_name, bases_name)
        for name in check2:
            logging.info(name)

    def set_targetstats(self, ltable_args: Tuple[str, str], rtable_args: Tuple[str, str], tableindex: int):
        """
        Sets BaseMorph.target_stats to the pd.[DataFrame|Series] per clsrecon_dict.

        ltable_url, lpkey = ltable_args
        rtable_url, to_col = rtable_args
        lpkey |-(clsrecon_dict)-> from_col === to_col
        """
        logging.info("BaseMorph.set_targetstats(self, %s, %s)", ltable_args, rtable_args)
        # unpack arguments
        ltable_url, lpval = ltable_args
        rtable_url, to_col = rtable_args
        # load clsrecon_dict from json
        ltable_name = self.page_dict[ltable_url]
        rtable_name = self.page_dict[rtable_url]
        json_path = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        with open(str(json_path), encoding='utf-8') as rfile:
            clsrecon_dict = json.load(rfile)
        from_col = clsrecon_dict[lpval]
        if from_col is None:
            self.target_stats = None
        else:
            self.target_stats = self.url_to_tables[rtable_url][tableindex].set_index(to_col).loc[from_col, :]

if __name__ == '__main__':
    pass
