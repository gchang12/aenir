#!/usr/bin/python3
"""
Defines methods for reconciling names for table-pairs of the following varieties:
- Character-to-Class
- Class-to-Class
- Character-to-Character
"""

from typing import Mapping

from aenir.cleaner import SerenesCleaner


class SerenesReconciler(SerenesCleaner):
    """
    Defines methods for identifying names present in the column of one table,
    and mapping those names to those of a column in another.
    """
    def __init__(self, game_num):
        """
        """
        pass

    def create_chr_to_cls_reconfile(self, table_col: [(fromtable, fromcol), (totable, tocol)]):
        """
        """
        pass

    def create_cls_to_cls_reconfile(self):
        """
        """
        pass

    def create_chr_to_chr_reconfile(self):
        """
        """
        pass


if __name__ == '__main__':
    pass
