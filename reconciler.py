#!/usr/bin/python3
"""
Defines methods for reconciling names for table-pairs of the following varieties:
- Character-to-Class
- Class-to-Class
- Character-to-Character
"""

from typing import Tuple

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
        pass

    def get_namerecon_json(self, ltable: str, rtable: str):
        """
        Returns a pathlib.Path of the form, ltable_JOIN_rtable
        """
        namerecon_table = self.URL_TO_TABLE[ltable] + "_JOIN_" + self.URL_TO_TABLE[rtable] + ".json"
        return self.get_datafile_path(namerecon_table)

    def create_namerecon_file(self, ltable_columns: Tuple[str, str, str], rtable_column: Tuple[str, str]):
        """
        Create name recon file.
        Fail if it exists
        """
        # ltable_columns: (ltable, from_col, tomatch_col)
        # rtable_column: (rtable, to_col)
        pass

if __name__ == '__main__':
    pass
