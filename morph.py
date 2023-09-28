#!/usr/bin/python3
"""
Defines Morph class.

Morph: Defines methods to simulate level-ups and promotions for FE units, excluding FE4 kids.
"""

import logging

import pandas as pd

from aenir._basemorph import BaseMorph

class Morph(BaseMorph):
    """
    """

    # declare promo-branch exceptions here as a dict-attribute
    _BRANCHED_PROMO_EXCEPTIONS = {
            (4, "Ira"): "Swordmaster",
            (4, "Holyn"): "Forrest",
            (4, "Radney"): "Swordmaster",
            (4, "Roddlevan"): "Forrest",
            (4, "Azel"): "Mage Knight",
            (4, "Arthur"): "Mage Knight",
            (4, "Tinny"): "Mage Fighter (F)",
            (5, "Rifis"): "Thief Fighter",
            (5, "Asvel"): "Sage",
            (5, "Miranda"): "Mage Knight",
            (5, "Tania"): "Sniper (F)",
            (5, "Ronan"): "Sniper (M)",
            (5, "Machua"): "Mercenary",
            (5, "Shiva"): "Swordmaster",
            (5, "Mareeta"): "Swordmaster",
            (5, "Trewd"): "Swordmaster",
            }

    def __init__(self, game_num: int, unit_name: str, tableindex: int = 0):
        """
        """
        BaseMorph.__init__(self, game_num)
        self.unit_name = unit_name
        # load tables
        #self.home_dir = Path() # In case I need to change the directory for when I upload this
        self.tables_file = "cleaned_stats.db"
        for urlpath in self.page_dict:
            self.load_tables(urlpath)
        # initialize bases
        temp_bases = self.url_to_tables["characters/base-stats"][tableindex].set_index("Name").loc[unit_name, :]
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

    def level_up(self, target_lv: int, tableindex: int = 0):
        """
        """
        self.set_targetstats(
                ("characters/base-stats", self.unit_name),
                ("characters/growth-rates", "Name"),
                tableindex,
                )
        temp_growths = self.target_stats.reindex(self.current_stats.index, fill_value=0.0)
        self.current_stats += (temp_growths / 100) * (target_lv - self.current_lv)

    def get_minpromolv(self):
        """
        """
        if self.game_num == 4:
            minpromolv = 20
        elif (self.game_num, self.unit_name, self.promo_cls) == (5, "Lara", "Dancer"):
            minpromolv = 1
        else:
            try:
                minpromolv = {
                        (6, "Roy"): 1,
                        (7, "Hector"): 1,
                        (7, "Eliwood"): 1,
                        (5, "Linoan"): 1,
                        (5, "Leif"): 1,
                        }[(self.game_num, self.unit_name)]
            except KeyError:
                minpromolv = 10
        return minpromolv

    def get_maxlv(self):
        """
        """
        if self.game_num == 4:
            maxlv = 30
        elif self.unit_name in ("Ross", "Amelia", "Ewan") and not self.history:
            maxlv = 10
        else:
            maxlv = 20
        return maxlv

    def promote(self, tableindex: int = 0):
        """
        """
        if self.current_clstype == "characters/base-stats":
            lpval = self.unit_name
        elif self.current_clstype == "classes/promotion-gains":
            lpval = self.current_cls
        self.set_targetstats(
                (self.current_clstype, lpval),
                ("classes/promotion-gains", "Class"),
                tableindex,
                )
        if self.target_stats is None:
            raise ValueError(f"{self.unit_name} has no available promotions.")
        old_cls = self.current_cls
        if isinstance(self.target_stats, pd.DataFrame):
            self.target_stats = self.target_stats.set_index("Promotion").loc[self.promo_cls, :]
            # raises KeyError for split-promotions; utilize to advantage
            self.current_cls = self.target_stats.name
        else:
            self.current_cls = self.target_stats.pop("Promotion")
        self.history.append( (self.old_cls, self.current_lv) )
        self.promo_cls = None
        self.current_clstype = "classes/promotion-gains"
        temp_promo = self.target_stats.reindex(self.current_stats.index, fill_value=0.0)
        self.current_stats += temp_promo
        if self.game_num != 4:
            self.current_lv = 1

    def cap_stats(self, tableindex: int = 0):
        """
        """
        if self.current_clstype == "characters/base-stats":
            lpval = self.unit_name
        elif self.current_clstype == "classes/promotion-gains":
            lpval = self.current_cls
        self.set_targetstats(
                (self.current_clstype, lpval),
                ("classes/maximum-stats", "Class"),
                tableindex,
                )
        temp_maxes = self.target_stats.reindex(self.current_stats.index, fill_value=0.0)
        self.current_stats.mask(self.current_stats > temp_maxes, inplace=True)

if __name__ == '__main__':
    pass
