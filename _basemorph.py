#!/usr/bin/python3
"""
"""

from aenir.cleaner import SerenesCleaner

class BaseMorph(SerenesCleaner):
    def __init__(self, game_num, unit_name):
        SerenesCleaner.__init__(self, game_num)
        for urlpath in self.page_dict:
            self.load_tables(urlpath)
        for tbl_index, table in enumerate(self.url_to_tables["characters/base-stats"]):
            if unit_name not in table.loc[:, "Name"]:
                continue
            break
        self.tbl_index = tbl_index
        self.current_clstype = "characters/base-stats"
        #self.current_stats = self.url_to_tables["characters/base-stats"][self.tbl_index].set_index("Name").loc[unit_name, :].copy()
        #self.current_lv = self.current_stats.pop("Lv")
        #self.current_cls = self.current_stats.pop("Class")
        #self.current_stats += 0.0

    def level_up(self, num_levels):
        # foreign key = Name
        # try: json_dict[Name]
        # except KeyError: foreign_iey =current_cls
        # current_stats += (growths/100).setfield(bases).fillna(0)
        # foreign key = Class
        # constrain current_stats to maxes[Class]
        pass

    def promote(self):
        # foreignkey = Class
        # current_stats += promo_class[Class].setfield(bases).fillna(0)
        # current_cls=promo_cls[Class]
        # current_clstype=classes/max-stats
        # foreignkey=Class
        # constrain current_stats to maxes[Class]
        # reset level
        pass

    def get_max_level(self):
        pass

if __name__ == '__main__':
    pass 
