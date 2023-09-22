#!/usr/bin/python3
"""
"""

from typing import Union, Tuple, List

from aenir._basemorph import BaseMorph

class ProtoMorph(BaseMorph):
    def __init__(self, game_num: int, unit_name: Union[str, Tuple[str, str]], unit_col: List[str], tableindex: int):
        BaseMorph.__init__(self, game_num)
        BaseMorph.set_targetstats("characters/base-stats", unit_name, unit_col, tableindex)
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

    def promote(self, tableindex: int, promocls: str):
        self.set_targetstats("classes/promotion-gains", self.unit_name, ["Class"], tableindex)
        self.target_stats.pop(["Promotion"])
        self.target_stats.reindex(index=self.current_stats.index, fill_value=0.0)
        self.current_stats += self.target_stats * 1.0
        self.current_clstype = "classes/promotion-gains"

    def cap_stats(self, tableindex: int):
        self.set_targetstats("classes/maximum-stats", self.unit_name, ["Class"], tableindex)
        self.target_stats.reindex(index=self.current_stats.index, fill_value=0.0)
        self.current_stats.where(
                self.current_stats > self.target_stats,
                other=self.target_stats,
                inplace=True
                )

if __name__ == '__main__':
    pass
