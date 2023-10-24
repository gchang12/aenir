#!/usr/bin/python3
"""
Defines Morph class.

Morph: Defines methods to simulate level-ups and promotions for FE units, excluding FE4 kids.
"""

import logging
from collections import OrderedDict
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
            (4, "Lakche"): "Swordmaster",
            (4, "Skasaher"): "Forrest",
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
        BaseMorph.__init__(self, game_num, datadir_root)
        # initialize bases
        self._unit_name = unit_name
        temp_bases = self.url_to_tables["characters/base-stats"][tableindex].set_index("Name").loc[unit_name, :]
        logging.info("Morph(%d, '%s')", game_num, unit_name)
        self.current_clstype = "characters/base-stats"
        self.current_cls = temp_bases.pop("Class")
        self.current_lv = temp_bases.pop("Lv")
        # implicitly convert to float
        self.current_stats = temp_bases + 0.0
        try:
            self.promo_cls = self._BRANCHED_PROMO_EXCEPTIONS[(game_num, unit_name)]
        except KeyError:
            self.promo_cls = None
        # test if unit has HM bonus
        if " (HM)" in unit_name or unit_name + " (HM)" in self.get_character_list():
            self.comparison_labels["Hard Mode"] = " (HM)" in unit_name

    @property
    def unit_name(self) -> str:
        """
        The name of the unit whose stats are to be queried.
        """
        return self._unit_name

    @property
    def BRANCHED_PROMO_EXCEPTIONS(self) -> dict:
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
                error_msg = f"The target level of {target_lv} is less than or equal to the current level of {self.current_lv}."
            raise ValueError(error_msg + " Aborting.")
        self.set_targetstats(
                ("characters/base-stats", self.unit_name),
                ("characters/growth-rates", "Name"),
                tableindex,
                )
        logging.info("Morph.level_up(%d, tableindex=%d)", target_lv, tableindex)
        temp_growths = self.target_stats.reindex(self.current_stats.index, fill_value=0.0)
        self.current_stats += (temp_growths / 100) * (target_lv - self.current_lv)
        self.current_lv = target_lv

    def get_minpromolv(self) -> int:
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

    def get_maxlv(self) -> int:
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
        logging.info("Morph.promote(tableindex=%d)", tableindex)
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
        logging.info("Morph.cap_stats(tableindex=%d)", tableindex)
        temp_maxes = self.target_stats.reindex(self.current_stats.index, fill_value=0.0) * 1.0
        self.current_stats.mask(self.current_stats > temp_maxes, other=temp_maxes, inplace=True)

    def is_maxed(self, tableindex: int = 0) -> pd.Series:
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
        logging.info("Morph.is_maxed(tableindex=%d)", tableindex)
        temp_maxes = self.target_stats.reindex(self.current_stats.index, fill_value=0.0) * 1.0
        return temp_maxes == self.current_stats

    def __repr__(self) -> str:
        """
        Returns a pd.Series-str summarizing the stats, history, and more about a Morph instance.

        Raises:
        - no errors, hurrah!

        Returns a pd.Series-str of the form:
        - Name
        - {history}
        - Class
        - Lv
        - {numeric_stats}
        """
        return self.get_repr_series().to_string()

    def get_repr_series(self) -> pd.Series:
        """
        Creates the pd.Series for implementation in the __repr__ dunder.

        See Morph.__repr__ docstring for more information.
        """
        # create header rows
        header_rows = OrderedDict()
        header_rows["Name"] = self.unit_name
        for index, entry in enumerate(self.history):
            header_rows["PrevClassLv" + str(index + 1)] = entry
        header_rows["Class"] = self.current_cls
        header_rows["Lv"] = self.current_lv
        header_rows.update(self.comparison_labels)
        repr_series = pd.concat([pd.Series(header_rows), self.current_stats])
        repr_series.name = self.unit_name
        return repr_series

    def __lt__(self, other) -> pd.DataFrame:
        """
        Returns a pd.DataFrame summarizing the difference between one Morph and another.

        Raises:
        - no errors, hurrah!

        Returned pd.DataFrame is of the form:
        - {history}
        - Class
        - Lv
        - {numeric_stats}

        with name = self.unit_name
        """
        # create stat_df
        if other.current_stats.name == self.current_stats.name:
            other.current_stats.name += " (2)"
        diff = other.current_stats - self.current_stats
        diff.name = 'is-less_than-by'
        stat_df = pd.concat(
            [
                self.current_stats,
                diff,
                other.current_stats,
            ],
            axis=1,
        )
        # create clslv_rows
        self_clslv = [self.current_cls, self.current_lv]
        other_clslv = [other.current_cls, other.current_lv]
        # create history_rows
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
            index=["PrevClassLv" + str(index + 1) for index in range(max_histlen)] + ['Class', 'Lv']
        )
        # create rows for comparison_labels
        meta_labels = []
        for row_label in self.comparison_labels:
            if row_label in meta_labels:
                continue
            meta_labels.append(row_label)
        for row_label in other.comparison_labels:
            if row_label in meta_labels:
                continue
            meta_labels.append(row_label)
        meta_map = {
            self.current_stats.name: [],
            diff.name: [],
            other.current_stats.name: [],
        }
        for row_label in meta_labels:
            if row_label in self.comparison_labels:
                comparison_val = self.comparison_labels[row_label]
            else:
                comparison_val = "-"
            meta_map[self.current_stats.name].append(comparison_val)
            if row_label in other.comparison_labels:
                comparison_val = other.comparison_labels[row_label]
            else:
                comparison_val = "-"
            meta_map[other.current_stats.name].append(comparison_val)
            meta_map[diff.name].append("-")
        meta_rows = pd.DataFrame(meta_map, index=meta_labels)
        other.current_stats.name = other.current_stats.name.replace(" (2)", "")
        return pd.concat([meta_rows, clslv_df, stat_df])


class Morph4(Morph):
    """
    Inherits: aenir.morph.Morph.

    Modifies existing methods for collection of units in FE4.
    """

    def __init__(self, unit_name: str, father_name: str = None, *, datadir_root: str = None):
        """
        Extends: Morph.__init__ (conditionally).

        FE4 child unit parameters are reinitialized using methods adopted from Morph superclass.
        Defines: father_name
        """
        game_num = 4
        BaseMorph.__init__(self, game_num, datadir_root)
        # inherits from Morph, which declares this a property
        #self.unit_name = unit_name
        kid_tableindex = 1
        self.is_kid = unit_name in self.url_to_tables["characters/base-stats"][kid_tableindex]["Name"].to_list()
        if self.is_kid:
            self._father_name = father_name
        else:
            self._father_name = None
        logging.info("Morph4('%s', '%s')", unit_name, father_name)
        if self.is_kid:
            # initialize bases
            temp_bases = self.url_to_tables["characters/base-stats"][kid_tableindex].set_index(["Name", "Father"]).loc[(unit_name, father_name), :]
            self.current_cls = temp_bases.pop("Class")
            self.current_lv = temp_bases.pop("Lv")
            self.current_stats = temp_bases + 0.0
            self.current_stats.name = unit_name
            self._unit_name = unit_name
            self.current_clstype = "characters/base-stats"
            # implicitly convert to float
            self.comparison_labels = {"Father": father_name}
        else:
            Morph.__init__(self, game_num, unit_name, tableindex=0)
        try:
            self.promo_cls = self._BRANCHED_PROMO_EXCEPTIONS[(game_num, unit_name)]
        except KeyError:
            self.promo_cls = None

    @property
    def unit_name(self) -> str:
        """
        The name of the unit whose stats are to be queried.
        """
        return self._unit_name

    @property
    def father_name(self) -> str:
        """
        The name of the father of the unit whose stats are to be queried.
        """
        return self._father_name

    def level_up(self, target_lv: int):
        """
        Extends: Morph.level_up (conditionally).

        Method for FE4 kids has a different implementation.
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
        logging.info("Morph4.level_up(%d)", target_lv)
        tableindex = (1 if self.is_kid else 0)
        if self.is_kid:
            self.target_stats = self.url_to_tables["characters/growth-rates"][tableindex].set_index(["Name", "Father"]).loc[(self.unit_name, self.father_name), :]
            temp_growths = self.target_stats.reindex(self.current_stats.index, fill_value=0.0)
            self.current_stats += (temp_growths / 100) * (target_lv - self.current_lv)
            self.current_lv = target_lv
        else:
            Morph.level_up(self, target_lv, tableindex=tableindex)


class Morph5(Morph):
    """
    Inherits: aenir.morph.Morph.
   
    Defines promotion exceptions, and extends level_up method.
    """

    def __init__(self, unit_name: str, *, datadir_root: str = None):
        """
        Extends: Morph.__init__.

        Defines: equipped_scrolls := List[str]
        """
        game_num = 5
        Morph.__init__(self, game_num, unit_name, tableindex=0, datadir_root=datadir_root)
        self.equipped_scrolls = []

    def promote(self):
        """
        Extends: Morph.promote.

        Defines exceptions for Lara, who has two different promotion paths:
        - Thief -> Thief Fighter -> Dancer -> Thief Fighter
        - Thief -> Dancer -> Thief Fighter
        Ensures that Parne and Lifis don't promote into Dancers.
        Ensures that Lara receives the right promotions.
        """
        logging.info("Morph5.promote()")
        clslist = (cls for cls, lv in self.history)
        if self.current_cls == "Thief Fighter" and self.unit_name != "Lara":
            raise ValueError(f"{self.unit_name} has no available promotions.")
        elif self.unit_name == "Lara" and "Dancer" in clslist:
            raise ValueError(f"{self.unit_name} has no available promotions.")
        Morph.promote(self)

    def level_up(self, target_lv: int):
        """
        Extends: Morph.level_up

        Enables user to simulate scroll-boosted level-ups if equipped_scrolls list parameter is valid.
        """
        # pasted from Morph.level_up
        if target_lv > self.get_maxlv() or target_lv <= self.current_lv:
            if target_lv > self.get_maxlv():
                error_msg = f"The target level of {target_lv} exceeds the max level of {self.get_maxlv()}."
            else:
                error_msg = f"The target level of {target_lv} is less than or equal to the current level of {self.current_lv}."
            raise ValueError(error_msg + " Aborting.")
        if self.equipped_scrolls:
            temp_scrollbonus = pd.Series(index=self.current_stats.index, data=[0.0 for label in self.current_stats.index])
            # fetch table name, and table file
            save_path = self.home_dir.joinpath(self.tables_file)
            if not save_path.exists():
                raise FileNotFoundError(f"'{str(save_path)}' does not exist. Aborting.")
            save_file = str(save_path)
            table_name = "crusader_scrolls"
            con = "sqlite:///" + save_file
            scroll_table = pd.read_sql_table(table_name, con).set_index("Name")
            # accumulate bonuses
            for scroll_name in self.equipped_scrolls:
                try:
                    temp_scrollbonus += scroll_table.loc[scroll_name, :]
                except KeyError as keyerr:
                    print(f"'{scroll_name}' is not a valid Crusader name. Choose from the list:")
                    for crusader_name in scroll_table.index:
                        print("'" + crusader_name + "'")
                    raise keyerr
            # cap bonus at zero if growths < 0
            temp_scrollbonus.mask(temp_scrollbonus < 0, other=0, inplace=True)
            # increment
            self.current_stats += (temp_scrollbonus / 100) * (target_lv - self.current_lv)
        Morph.level_up(self, target_lv)

class Morph7(Morph):
    """
    Inherits: aenir.morph.Morph. Serves mainly to accommodate for Lyn Mode units.
    """

    def __init__(self, unit_name: str, lyn_mode: bool = False, *, datadir_root: str = None):
        """
        Extends: Morph.__init__.

        - Adds promotion exception for Wallace
        - Allows user to choose Lyn Mode or otherwise
        """
        game_num = 7
        # if the user lists a non-LM unit, but puts lyn_mode=True, the program halts
        Morph.__init__(self, game_num, unit_name, tableindex=(0 if lyn_mode else 1), datadir_root=datadir_root)
        logging.info("Morph7.__init__('%s', %s, %s)", unit_name, lyn_mode, datadir_root)
        self.lyn_mode = None
        if unit_name in self.url_to_tables["characters/base-stats"][0].loc[:, "Name"].to_list():
            self.comparison_labels.update({"Campaign": ("Main" if not lyn_mode else "Tutorial")})
            self.lyn_mode = lyn_mode
        if not lyn_mode and unit_name == "Wallace":
            # must add in line with 'General (M)' -> None in promo-JOIN-promo JSON file
            self.current_clstype = "classes/promotion-gains"


# to interface with web-deploy layer better.
class Morph6(Morph):
    """
    Inherits: aenir.morph.Morph
    """
    def __init__(self, unit_name: str, datadir_root: str = None):
        """
        Extends: Morph.__init__
        - game_num: 6
        """
        game_num = 6
        Morph.__init__(self, game_num, unit_name, tableindex=0, datadir_root=datadir_root)


class Morph8(Morph):
    """
    Inherits: aenir.morph.Morph
    """
    def __init__(self, unit_name: str, datadir_root: str = None):
        """
        Extends: Morph.__init__
        - game_num: 8
        """
        game_num = 8
        Morph.__init__(self, game_num, unit_name, tableindex=0, datadir_root=datadir_root)


class Morph9(Morph):
    """
    Inherits: aenir.morph.Morph
    """
    def __init__(self, unit_name: str, datadir_root: str = None):
        """
        Extends: Morph.__init__
        - game_num: 9
        """
        game_num = 9
        Morph.__init__(self, game_num, unit_name, tableindex=0, datadir_root=datadir_root)


if __name__ == '__main__':
    pass
