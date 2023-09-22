#!/usr/bin/python3
"""
"""

from typing import Union, Tuple, List

from aenir._basemorph import BaseMorph

class Morph(BaseMorph):
    def __init__(self, game_num: int, unit_name: str, tableindex: int):
        BaseMorph.__init__(self, game_num)
        BaseMorph.set_targetstats("characters/base-stats", unit_name, ["Name"], tableindex)
        self.unit_name = unit_name
        self.current_stats = self.target_stats
        self.current_cls = self.current_stats.pop("Class")
        self.current_lv = self.current_stats.pop("Lv")
        # implicit conversion to float-df
        self.current_stats += 0.0

    def level_up(self, num_levels: int, tableindex: int):
        self.set_targetstats("characters/growth-rates", self.unit_name, ["Name"], tableindex)
        # adjust the pd.Series to match self.current_stats
        self.target_stats.reindex(index=self.current_stats.index, fill_value=0.0)
        self.current_stats += (self.target_stats / 100) * num_levels

    def promote(self, promocls: str):
        if self.current_clstype.startswith("characters/"):
            home_pval = self.unit_name
        elif self.current_clstype.startswith("classes/"):
            home_pval = self.current_cls
        self.set_targetstats("classes/promotion-gains", home_pval, ["Class"], 0)
        if isinstance(self.target_stats, pd.DataFrame):
            # use promocls here
            pass
        self.current_cls = self.target_stats.pop(["Promotion"])
        self.target_stats.reindex(index=self.current_stats.index, fill_value=0.0)
        self.current_stats += self.target_stats * 1.0
        self.current_clstype = "classes/promotion-gains"

    def cap_stats(self, tableindex: int):
        if self.current_clstype.startswith("characters/"):
            home_pval = self.unit_name
        elif self.current_clstype.startswith("classes/"):
            home_pval = self.current_cls
        self.set_targetstats("classes/maximum-stats", home_pval, ["Class"], tableindex)
        self.target_stats.reindex(index=self.current_stats.index, fill_value=0.0)
        self.current_stats.where(
                self.current_stats > self.target_stats,
                other=self.target_stats,
                inplace=True
                )

if __name__ == '__main__':
    pass
