#!/usr/bin/python3
"""
Defines methods for reconciling names for table-pairs of the following varieties:
- Character-to-Class
- Class-to-Class
- Character-to-Character
"""

from typing import Tuple
import json
import logging

from aenir.cleaner import SerenesCleaner


class SerenesReconciler(SerenesCleaner):
    """
    Defines methods for identifying names present in the column of one table,
    and mapping those names to those of a column in another.
    """

    def __init__(self, game_num):
        """
        Create object
        """
        SerenesCleaner.__init__(self, game_num)

    def get_namerecon_json(self, ltable: str, rtable: str):
        """
        Returns a pathlib.Path of the form, ltable_JOIN_rtable
        """
        namerecon_table = self.URL_TO_TABLE[ltable] + "_JOIN_" + self.URL_TO_TABLE[rtable] + ".json"
        return self.get_datafile_path(namerecon_table)

    def create_namerecon_file(self, ltable_columns: Tuple[str, str, str], rtable_columns: Tuple[str, str]):
        """
        Create name recon file.
        Fail if it exists
        """
        ltable, key_col, from_col = ltable_columns
        rtable, to_col = rtable_columns
        namerecon_dict = {}
        nnamerecon_dict = {}
        namerecon_json = self.get_namerecon_json(ltable, rtable)
        if namerecon_json.exists():
            logging.info("namerecon_json exists")
            raise FileExistsError
        logging.info("Compiling column-pairs")
        for ltable_df in self.url_to_tables[ltable]:
            for index in ltable_df.index:
                pkey = ltable_df.at[index, key_col]
                pval = ltable_df.at[index, from_col]
                namerecon_dict[pkey] = pval
        # gather set from right table.
        # subtract right from left set.
        logging.info("Compiling non-matching column-pairs")
        for rtable_df in self.url_to_tables[rtable]:
            for index in rtable_df.index:
                if rtable_df.at[index, to_col] not in namerecon_dict.values():
                    continue
                for pkey, pval in namerecon_dict.items():
                    if pval == rtable_df.at[index, to_col]:
                        continue
                    nnamerecon_dict[pkey] = None
        with open(str(namerecon_json), mode='w', encoding='utf-8') as wfile:
            json.dump(nnamerecon_dict, wfile)

if __name__ == '__main__':
    pass
