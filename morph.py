#!/usr/bin/python3
"""
Defines Morph class.

Morph: Defines methods to simulate level-ups and promotions for FE units, excluding FE4 kids.
"""

import logging
from pathlib import Path

import pandas as pd

from aenir._basemorph import BaseMorph

class Morph(BaseMorph):
    """
    Defines methods to simulate level-ups and promotions for interactive user session.

    BRANCHED_PROMO_EXCEPTIONS: dict of fixed promotion paths, filled out manually.
    unit_name: The name of the unit.
    promo_cls: Determines which promotion path the unit must follow.
    current_stats: Stores the unit's current stats; the centerpiece, and object of most operations.
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

    def __init__(self, game_num: int, unit_name: str, *, tableindex: int = 0, datadir_root: str = None):
        """
        Loads tables, and initializes bases among other things.

        Defines: promo_cls, unit_name, current_stats
        """
        BaseMorph.__init__(self, game_num)
        self.unit_name = unit_name
        # load tables
        if type(datadir_root) == str:
            self.home_dir = Path(datadir_root).joinpath(self.game_name)
        self.tables_file = "cleaned_stats.db"
        for urlpath in self.page_dict:
            self.load_tables(urlpath)
        # initialize bases
        logging.info("Morph(%d, '%s')", game_num, unit_name)
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
        Resolves from_col name conflicts when promoting certain units.
        """
        return self._BRANCHED_PROMO_EXCEPTIONS

    def level_up(self, target_lv: int, tableindex: int = 0):
        """
        Increases unit's level, and increments current_stats accordingly.

        Raises:
        - ValueError: (target_lv <= current_lv) or (target_lv > max_lv)
        """
        if target_lv > self.get_maxlv() or target_lv <= self.current_lv:
            if target_lv > self.get_maxlv():
                error_msg = f"The target level of {target_lv} exceeds the max level of {self.get_maxlv()}."
            else:
                error_msg = f"The target level of {target_lv} is less than the current level of {self.current_lv}."
            raise ValueError(error_msg + " Aborting.")
        self.set_targetstats(
                ("characters/base-stats", self.unit_name),
                ("characters/growth-rates", "Name"),
                tableindex,
                )
        temp_growths = self.target_stats.reindex(self.current_stats.index, fill_value=0.0)
        self.current_stats += (temp_growths / 100) * (target_lv - self.current_lv)
        self.current_lv = target_lv

    def get_minpromolv(self):
        """
        Determines the minimum promotion level for a given unit.

        All exceptional units are logged here.
        """
        if self.game_num == 4:
            minpromolv = 20
        elif (self.game_num, self.unit_name, self.promo_cls) == (5, "Lara", "Dancer"):
            # for Lara shenanigans
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
        Determines the maximum level for a given unit.
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
        Applies promotion bonuses, then changes classes.

        Raises:
        - ValueError: Minimum promotion level not attained.
        - ValueError: Unit cannot promote.
        Sets:
        - current_stats += promo_bonus
        - history += (old_class, old_lv)
        - promo_cls = None
        - current_clstype = 'classes/promotion-gains'
        """
        if self.current_clstype == "characters/base-stats":
            lindex_val = self.unit_name
        elif self.current_clstype == "classes/promotion-gains":
            lindex_val = self.current_cls
        self.set_targetstats(
                (self.current_clstype, lindex_val),
                ("classes/promotion-gains", "Class"),
                tableindex,
                )
        if self.target_stats is None:
            raise ValueError(f"{self.unit_name} has no available promotions.")
        if self.current_lv < self.get_minpromolv():
            raise ValueError(f"{self.unit_name} must be at least level {self.get_minpromolv()} to promote. Current level: {self.current_lv}")
        old_cls = self.current_cls
        if isinstance(self.target_stats, pd.DataFrame):
            self.target_stats = self.target_stats.set_index("Promotion").loc[self.promo_cls, :]
            # raises KeyError for split-promotions; utilize to advantage (i.e. SELECT from target_stats.loc[:, "Promotion"])
            self.current_cls = self.target_stats.name
        else:
            self.current_cls = self.target_stats.pop("Promotion")
        self.history.append( (old_cls, self.current_lv) )
        self.promo_cls = None
        self.current_clstype = "classes/promotion-gains"
        temp_promo = self.target_stats.reindex(self.current_stats.index, fill_value=0.0) * 1.0
        self.current_stats += temp_promo
        if self.game_num != 4:
            self.current_lv = 1

    def cap_stats(self, tableindex: int = 0):
        """
        Caps a unit's current_stats in accordance with the class's maximum stats.
        """
        if self.current_clstype == "characters/base-stats":
            lindex_val = self.unit_name
        elif self.current_clstype == "classes/promotion-gains":
            lindex_val = self.current_cls
        self.set_targetstats(
                (self.current_clstype, lindex_val),
                ("classes/maximum-stats", "Class"),
                tableindex,
                )
        temp_maxes = self.target_stats.reindex(self.current_stats.index, fill_value=0.0) * 1.0
        self.current_stats.mask(self.current_stats > temp_maxes, other=temp_maxes, inplace=True)

    def is_maxed(self, tableindex: int = 0):
        """
        Returns a pd.Series showing which of the Morph's stats are maxed.
        """
        if self.current_clstype == "characters/base-stats":
            lindex_val = self.unit_name
        elif self.current_clstype == "classes/promotion-gains":
            lindex_val = self.current_cls
        self.set_targetstats(
                (self.current_clstype, lindex_val),
                ("classes/maximum-stats", "Class"),
                tableindex,
                )
        temp_maxes = self.target_stats.reindex(self.current_stats.index, fill_value=0.0) * 1.0
        return temp_maxes == self.current_stats

    def __lt__(self, other):
        """
        Returns a pd.DataFrame summarizing the difference between one Morph and another.

        Raises:
        - no errors, hurrah!

        Returned pd.DataFrame is of the form:
        - History
        - Class
        - Lv
        - {numeric_stats}
        """
        diff = other.current_stats - self.current_stats
        diff.name = 'is-less_than-by'
        # create rows for class and level
        self_clslv = [self.current_cls, self.current_lv]
        other_clslv = [other.current_cls, other.current_lv]
        # create rows for history
        max_histlen = max([len(self.history), len(other.history)])
        for index in range(max_histlen):
            self_clslv.insert(0, "-")
            other_clslv.insert(0, "-")
        for index, entry in enumerate(self.history):
            self_clslv[index] = entry
        for index, entry in enumerate(other.history):
            other_clslv[index] = entry
        clslv_df = pd.DataFrame(
            {
                self.current_stats.name: self_clslv,
                diff.name: ['-' for entry in self_clslv],
                other.current_stats.name: other_clslv,
            },
            index=["PrevClassLv" + str(index) for index in range(max_histlen)] + ['Class', 'Lv']
        )
        stat_df = pd.concat(
            [
                self.current_stats,
                diff,
                other.current_stats,
            ],
            axis=1
        )
        return pd.concat([clslv_df, stat_df])


class Morph4(Morph):
    """
    """

    def __init__(self, unit_name: str, father_name: str, *, datadir_root: str = None):
        """
        Loads tables, and initializes bases among other things.

        Implements...
        Defines: promo_cls, unit_name, current_stats
        """
        game_num = 4
        try:
            Morph.__init__(self, game_num, unit_name)
        except KeyError:
            pass
        logging.info("Morph(%d, '%s', '%s')", game_num, unit_name, father_name)
        self.father_name = father_name
        # initialize bases
        tableindex = 1
        temp_bases = self.url_to_tables["characters/base-stats"][tableindex].set_index(["Name", "Father"]).loc[(unit_name, father_name), :]
        self.current_clstype = "characters/base-stats"
        self.current_cls = temp_bases.pop("Class")
        self.current_lv = temp_bases.pop("Lv")
        # implicitly convert to float
        self.current_stats = temp_bases + 0.0
        try:
            self.promo_cls = self._BRANCHED_PROMO_EXCEPTIONS[(game_num, unit_name)]
        except KeyError:
            self.promo_cls = None

    def level_up(self, target_lv: int):
        """
        Increases unit's level, and increments current_stats accordingly.
        Implements...

        Raises:
        - ValueError: (target_lv <= current_lv) or (target_lv > max_lv)
        """
        if target_lv > self.get_maxlv() or target_lv <= self.current_lv:
            if target_lv > self.get_maxlv():
                error_msg = f"The target level of {target_lv} exceeds the max level of {self.get_maxlv()}."
            else:
                error_msg = f"The target level of {target_lv} is less than the current level of {self.current_lv}."
            raise ValueError(error_msg + " Aborting.")
        # target_stats is set directly instead via the usual method.
        tableindex = 1
        self.target_stats = self.url_to_tables["characters/growth-rates"][tableindex].set_index(["Name", "Father"]).loc[(self.unit_name, self.father_name), :]
        temp_growths = self.target_stats.reindex(self.current_stats.index, fill_value=0.0)
        self.current_stats += (temp_growths / 100) * (target_lv - self.current_lv)
        self.current_lv = target_lv


class Morph5(Morph):
    """
    """

    def __init__(self, unit_name: str, *, datadir_root: str = None):
        """
        """
        game_num = 5
        tableindex = 0
        Morph.__init__(game_num, unit_name, tableindex=tableindex, datadir_root=datadir_root)

    def promote(self):
        """
        """
        if self.current_cls == "Thief Fighter" and self.unit_name != "Lara":
            raise ValueError(f"{self.unit_name} has no available promotions.")
        elif self.unit_name == "Lara" and len(self.history == 3):
            raise ValueError(f"{self.unit_name} has no available promotions.")
        Morph.promote()


class Morph7(Morph):
    """
    Defines methods to simulate level-ups and promotions for interactive user session.
 
    Inherits: Morph
    - differs in that the Wallace exception is added.
    """

    def __init__(self, unit_name: str, lyn_mode: bool = False, *, datadir_root: str = None):
        """
        Implements: Morph.__init__

        - Adds Wallace exception
        - Allows user to choose Lyn Mode or otherwise
        """
        game_num = 7
        tableindex = (0 if lyn_mode else 1)
        Morph.__init__(self, 7, unit_name, tableindex=tableindex, datadir_root=datadir_root)
        if not lyn_mode and unit_name == "Wallace":
            # must add in line with 'General (M)' -> None in promo-JOIN-promo JSON file
            self.current_clstype = "classes/promotion-gains"

if __name__ == '__main__':
    pass
