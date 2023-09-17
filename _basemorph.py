#!/usr/bin/python3
"""
Defines the BaseMorph class.

BaseMorph:
"""

import json
from typing import Tuple, Union

from aenir.transcriber import SerenesTranscriber

PrimaryKey = Union[str, Tuple[str, str]]

class BaseMorph(SerenesTranscriber):
    """
    """

    def __init__(self, game_num: int, unit_name: PrimaryKey, primary_key: PrimaryKey, tableindex: int = 0):
        """
        """
        SerenesTranscriber.__init__(self, game_num)
        self.unit_name = unit_name
        self.primary_key = primary_key
        # load tables
        self.tables_file = "cleaned_stats.db"
        for urlpath in self.page_dict:
            self.load_tables(urlpath)
        temp_bases = self.url_to_tables["characters/base-stats"][tableindex].set_index(primary_key).loc[unit_name, :]
        # initialize bases
        self.current_cls = temp_bases.pop("Class")
        self.current_lv = temp_bases.pop("Lv")
        self.current_stats = temp_bases + 0.0 # convert to float
        # initialize parameters for class-matching
        self.current_clstype = "characters/base-stats"
        self.target_cls = None

    def set_targetcls(self, target_urlpath: str, source_pkey: PrimaryKey):
        """
        """
        # reference JSON file
        # figure out which target class to use to reference the target table
        ltable_name = self.page_dict[self.current_clstype]
        rtable_name = self.page_dict[self.current_clstype]
        clsrecon_json = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        with open(str(clsrecon_json), encoding='utf-8') as rfile:
            clsrecon_dict = json.load(rfile)
        try:
            self.target_cls = clsrecon_dict[primary_key]
        except KeyError:
            self.target_cls = primary_key

    def level_up(self, num_levels: int, primary_key: PrimaryKey = "Name", tableindex: int = 0):
        """
        """
        urlpath = "characters/growth-rates"
        self.set_targetcls(urlpath)
        temp_growths = self.url_to_tables[urlpath][tableindex].set_index(primary_key).loc[self.target_cls, :]
        self.current_lv += num_levels
        self.current_stats += temp_growths / 100 * num_levels

    def cap_stats(self, primary_key: PrimaryKey = "Class", tableindex: int = 0):
        """
        """
        urlpath = "classes/maximum-stats"
        self.set_targetcls(urlpath)
        temp_maxes = self.url_to_tables[urlpath][tableindex].set_index(primary_key).loc[self.target_cls, :]
        temp_maxes.pop("Class")
        # if cell > max: cell = max (pd-style)

    def promote(self, promo_class: str, primary_key: PrimaryKey = "Class", tableindex: int = 0):
        """
        """
        urlpath = "classes/promotion-gains"
        self.set_targetcls(urlpath)
        temp_promo = self.url_to_tables[urlpath][tableindex].set_index(primary_key).loc[self.target_cls, :]
        self.current_cls = temp_promo.pop("Promotion")
        self.current_stats += temp_promo

if __name__ == '__main__':
    pass
