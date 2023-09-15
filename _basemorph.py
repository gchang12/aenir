#!/usr/bin/python3
"""
"""

from aenir.transcriber import SerenesTranscriber

class BaseMorph(SerenesTranscriber):
    def __init__(self, game_num, unit_name):
        # cheated: created this code before the test code
        SerenesCleaner.__init__(self, game_num)
        self.current_clstype = "characters/base-stats"
        self.target_cls = None
        self.tables_file = "cleaned_stats.db"
        for urlpath in self.page_dict:
            self.load_tables(urlpath)
        # delete a bunch of methods

if __name__ == '__main__':
    pass 
