#!/usr/bin/python3
"""
"""

from aenir.morph import Morph

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
        tableindex = 1
        BaseMorph.__init__(self, game_num)
        self.unit_name = unit_name
        self.father_name = father_name
        logging.info("Morph(%d, '%s', '%s')", game_num, unit_name, father_name)
        # load tables
        if type(datadir_root) == str:
            self.home_dir = Path(datadir_root).joinpath(self.game_name)
        self.tables_file = "cleaned_stats.db"
        for urlpath in self.page_dict:
            self.load_tables(urlpath)
        # initialize bases
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
        tableindex = 1
        if target_lv > self.get_maxlv() or target_lv <= self.current_lv:
            if target_lv > self.get_maxlv():
                error_msg = f"The target level of {target_lv} exceeds the max level of {self.get_maxlv()}."
            else:
                error_msg = f"The target level of {target_lv} is less than the current level of {self.current_lv}."
            raise ValueError(error_msg + " Aborting.")
        # target_stats is set directly instead via the usual method.
        self.target_stats = self.url_to_tables["characters/growth-rates"][tableindex].set_index(["Name", "Father"]).loc[(self.unit_name, self.father_name), :]
        temp_growths = self.target_stats.reindex(self.current_stats.index, fill_value=0.0)
        self.current_stats += (temp_growths / 100) * (target_lv - self.current_lv)
        self.current_lv = target_lv

    def __lt__(self, other):
        """
        Implements...
        """
        comparison_df = Morph.__lt__(self, other)
        father_row = pd.DataFrame(
            {
                self.unit_name: [self.father_name],
                comparison_df.iloc[:, 1].name: ['-'],
                other.unit_name: [(other.father_name if isinstance(other, Morph4) else "-")],
            },
            index=['Father'],
        )
        return pd.concat( [father_row, comparison_df] )

if __name__ == '__main__':
    pass
