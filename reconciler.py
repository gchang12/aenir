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
        SerenesCleaner.__init__(self, game_num)
        pass

    def create_namerecon_file(self, ltable_columns: tuple, rtable_column: tuple):
        """
        """
        # ltable_columns: (ltable, from_col, tomatch_col)
        # rtable_column: (rtable, to_col)
        pass

    def sanitize_all_tables(self):
        """
        """
        # for each table:
        #    drop_nonnumeric_rows
        #    replace_with_int_df
        # try: create_fieldrecon_file
        # except FileNotExistsError: apply_fieldrecon_file
        pass

    def commit_namerecon_file(self, ltable_columns: tuple, rtable_column: tuple):
        """
        """
        pass


if __name__ == '__main__':
    pass
