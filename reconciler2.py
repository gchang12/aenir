#!/usr/bin/python3
"""
"""

from typing import Tuple
import json
import logging

from aenir.cleaner import SerenesCleaner


class SerenesReconciler(SerenesCleaner):
    """
    """

    def __init__(self, game_num):
        """
        """
        SerenesCleaner.__init__(self, game_num)

    def get_namerecon_json(self, ltable: str, rtable: str):
        """
        """
        namerecon_table = self.URL_TO_TABLE[ltable] + "-JOIN-" + self.URL_TO_TABLE[rtable] + ".json"
        return self.get_datafile_path(namerecon_table)

    def create_namerecon_file(self, ltable_columns: Tuple[str, str, str], rtable_columns: Tuple[str, str]):
        """
        """
        ltable, key_col, from_col = ltable_columns
        rtable, to_col = rtable_columns
        namerecon_dict = {}
        namerecon_json = self.get_namerecon_json(ltable, rtable)
        if namerecon_json.exists():
            raise FileExistsError
        for ltable_df in self.url_to_tables[ltable]:
            for index in ltable_df.index:
                pkey = ltable_df.at[index, key_col]
                pval = ltable_df.at[index, from_col]
                namerecon_dict[pkey] = pval
        rnamerecon_set = set()
        for rtable_df in self.url_to_tables[rtable]:
            rnamerecon_set.update(set(rtable_df.loc[:, to_col]))
        rnamerecon_dict = {}
        for pkey, pval in namerecon_dict.items():
            if pval in rnamerecon_set:
                continue
            rnamerecon_dict[pkey] = None
        with open(str(namerecon_json), mode='w', encoding='utf-8') as wfile:
            json.dump(rnamerecon_dict, wfile, indent=4)

    def verify_namerecons(self, ltable: str, rtable_columns: Tuple[str, str]):
        """
        """
        rtable, to_col = rtable_columns
        json_path = self.get_namerecon_json(ltable, rtable)
        with open(str(json_path), encoding='utf-8') as rfile:
            namerecon_dict = json.load(rfile)
        rtable_set = set()
        for rtable_df in self.url_to_tables[rtable]:
            rtable_set.update(set(rtable_df.loc[:, to_col]))
        nonexistent_values = set()
        for value in namerecon_dict.values():
            if value is None:
                continue
            if value not in rtable_set:
                nonexistent_values.add(value)
        if nonexistent_values:
            ne_value_str = "\n".join(nonexistent_values)
            return False
        else:
            return True

if __name__ == '__main__':
    pass
