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
        # essential to set_targetstats method
        self.current_clstype = "characters/base-stats"
        self.current_cls = None
        self.target_stats = None
        self.promo_index = None

    def verify_clsrecon_file(self, ltable_args: Tuple[str, str, str], rtable_args: Tuple[str, str]):
        """
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

if __name__ == '__main__':
    pass
