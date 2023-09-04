#!/usr/bin/python3
"""
Defines base class for Morph.
"""

import pandas as pd

from aenir.reconciler import SerenesReconciler

class BaseMorph(SerenesReconciler):
    """
    revenge match, let's go.
    """
    def __init__(self, game_num: int):
        # require: stat-table loading methods
        pass

    # elementary functions
    def modify_stats(self, increment: pd.Series):
        pass

    def change_class(self, clsname):
        # requires self.'promoclass' attribute to be set to non-None value
        pass

    def set_level(self, tgt_level: int):
        pass

    def get_maxlevel(self):
        pass

    def level_up(self, num_levels: int):
        self.set_level
        self.modify_stats

    def promote(self):
        # look up promo-class
        self.change_class
        pass

if __name__ == '__main__':
    pass
