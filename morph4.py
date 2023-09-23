#!/usr/bin/python3
"""
Defines Morph class.

Morph: Defines methods to simulate level-ups and promotions for FE units, excluding FE4 kids.
"""

import logging

import pandas as pd

from aenir._basemorph import BaseMorph

class Morph4(BaseMorph):
    """
    """

    # declare promo-branch exceptions here as a dict-attribute
    _BRANCHED_PROMO_EXCEPTIONS = {
            }

    # declare max-level exceptions?

    def __init__(self, game_num: int, unit_name: str, unit_father: str):
        """
        """
        BaseMorph.__init__(self, game_num)
        self.unit_name = unit_name
        # load tables
        self.tables_file = "cleaned_stats.db"
        for urlpath in self.page_dict:
            self.load_tables(urlpath)
        # initialize bases
        temp_bases = self.url_to_tables["characters/base-stats"][1].set_index(["Name", "Father"]).loc[(unit_name, unit_father), :]
        self.current_clstype = "characters/base-stats"
        self.current_cls = temp_bases.pop("Class")
        self.current_lv = temp_bases.pop("Lv")
        # implicitly convert to float
        self.current_stats = temp_bases + 0.0
        try:
            self.promo_cls = self._BRANCHED_PROMO_EXCEPTIONS[(game_num, unit_name)]
        except KeyError:
            self.promo_cls = None

    @property
    def BRANCHED_PROMO_EXCEPTIONS(self):
        """
        """
        return self._BRANCHED_PROMO_EXCEPTIONS

    def level_up(self, num_levels: int):
        """
        """
        self.set_targetstats(
                ("characters/base-stats", (self.unit_name, self.unit_father),
                ("characters/growth-rates", ["Name", "Father"]),
                1,
                )
        temp_growths = self.target_stats.reindex(self.current_stats.index, fill_value=0.0)
        self.current_stats += (temp_growths / 100) * num_levels

    def promote(self):
        """
        """
        if self.current_clstype == "characters/base-stats":
            lpval = self.unit_name
        elif self.current_clstype == "classes/promotion-gains":
            lpval = self.current_cls
        self.set_targetstats(
                (self.current_clstype, lpval),
                ("classes/promotion-gains", "Class"),
                0,
                )
        if self.target_stats is None:
            raise ValueError(f"{self.unit_name} has no available promotions.")
        if isinstance(self.target_stats, pd.DataFrame):
            self.target_stats = self.target_stats.set_index("Promotion").loc[self.promo_cls, :]
            self.current_cls = self.target_stats.name
        else:
            self.current_cls = self.target_stats.pop("Promotion")
        self.current_clstype = "classes/promotion-gains"
        temp_promo = self.target_stats.reindex(self.current_stats.index, fill_value=0.0)
        self.current_stats += temp_promo

    def cap_stats(self):
        """
        """
        if self.current_clstype == "characters/base-stats":
            lpval = self.unit_name
        elif self.current_clstype == "classes/promotion-gains":
            lpval = self.current_cls
        self.set_targetstats(
                (self.current_clstype, lpval),
                ("classes/maximum-stats", "Class"),
                0,
                )
        temp_maxes = self.target_stats.reindex(self.current_stats.index, fill_value=0.0)
        self.current_stats.mask(self.current_stats > temp_maxes, inplace=True)

if __name__ == '__main__':
    pass
