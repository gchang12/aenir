#!/usr/bin/python3
"""
Defines the BaseMorph class.

BaseMorph: Loads tables, and defines a method to simulate foreign-key lookup.
"""

from typing import Union, Tuple, List
import json
import io

from aenir.transcriber import SerenesTranscriber

class BaseMorph(SerenesTranscriber):
    """
    Defines methods to interface with stat database.

    Parameters:
    - current_clstype: Used in order to look-up name in class-recon dictionary.
    - target_stats: Stores stats that have been looked-up and stored.
    """

    def __init__(self, game_num: int):
        """
        Loads cleaned data, and sets parameters for class-lookup.
        """
        SerenesTranscriber.__init__(self, game_num)
        # load tables: Assume the cleaned_stats.db file exists
        self.tables_file = "cleaned_stats.db"
        for urlpath in self.page_dict:
            self.load_tables(urlpath)
        # initialize parameters for class-matching
        self.current_clstype = "characters/base-stats"
        self.current_cls = None
        self.target_stats = None

    def set_targetstats(self, target_urlpath: str, home_pval: Union[str, Tuple[str, str]], target_pkey: List[str], tableindex: int):
        """
        Looks up name in source table, and matches it to the target table via class-recon file.

        Sets target_stats attribute to appropriate value, depending on mapping.
        """
        #!current_clstype may not exist
        ltable_name = self.page_dict[self.current_clstype]
        rtable_name = self.page_dict[target_urlpath]
        # assume this file exists
        clsrecon_json = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        with io.open(str(clsrecon_json), encoding='utf-8') as rfile:
            clsrecon_dict = json.load(rfile)
        try:
            target_cls = clsrecon_dict[home_pval]
        except KeyError:
            target_cls = self.current_cls
        #!target_cls is None
        if target_cls is None:
            self.target_stats = None
        else:
            self.target_stats = self.url_to_tables[target_urlpath][tableindex].set_index(target_pkey).loc[target_cls, :]

if __name__ == '__main__':
    pass
