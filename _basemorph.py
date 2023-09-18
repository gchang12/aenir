#!/usr/bin/python3
"""
Defines the BaseMorph class.

BaseMorph: Loads tables, and defines a method to simulate foreign-key lookup.
"""

from typing import Union, Tuple
import json

from aenir.transcriber import SerenesTranscriber

class BaseMorph(SerenesTranscriber):
    """
    """

    def __init__(self, game_num: int):
        """
        """
        SerenesTranscriber.__init__(self, game_num)
        # load tables: Assume the cleaned_stats.db file exists
        self.tables_file = "cleaned_stats.db"
        for urlpath in self.page_dict:
            self.load_tables(urlpath)
        # initialize parameters for class-matching
        self.current_clstype = "characters/base-stats"
        self.target_stats = None

    def set_targetstats(self, target_urlpath: str, source_pkey: Union[str, Tuple[str, str]], tableindex: int):
        """
        # reference JSON file
        # figure out which target class to use to reference the target table
        """
        #!current_clstype may not exist
        ltable_name = self.page_dict[self.current_clstype]
        rtable_name = self.page_dict[self.current_clstype]
        # assume this file exists
        clsrecon_json = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        with open(str(clsrecon_json), encoding='utf-8') as rfile:
            clsrecon_dict = json.load(rfile)
        try:
            #!source_pkey not in clsrecon_dict
            target_cls = clsrecon_dict[source_pkey]
        except KeyError:
            target_cls = source_pkey
        #!target_cls is None
        if target_cls is None:
            self.target_stats = None
        else:
            self.target_stats = self.url_to_tables[target_urlpath][tableindex].set_index(source_pkey).loc[target_cls, :]

if __name__ == '__main__':
    pass
