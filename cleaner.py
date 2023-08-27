#!/usr/bin/python3
"""
Defines methods to clean up fields, null-rows, and non-int cells.
"""

from aenir.scraper import SerenesScraper
import re
import json

class SerenesCleaner(SerenesScraper):
    """
    Inherits: SerenesScraper.
    Defines methods for data cleanup process.
    """

    def __init__(self, game_num):
        """
        Defines filename to be manually filled
        for field cleanup process, in addition to parent
        attributes.
        """
        SerenesScraper.__init__(self, game_num, check_if_url_exists=False)
        self.fieldrecon_json = "fieldrecon.json"

    def replace_with_int_df(self, urlpath, columns):
        """
        Temporarily removes non-numeric columns.
        Converts numeric columns to those of the integer dtype.
        Reinserts non-numeric columns
        """

        def replace_with_int(cell):
            """
            Replaces a cell with itself cast to int.
            """
            new_cell = re.sub("[^0-9]*([0-9]+)[^0-9].*", "\\1", cell)
            if new_cell.isnumeric():
                return int(new_cell)
            else:
                return new_cell

        for index, table in enumerate(self.url_to_tables[urlpath]):
            nonnumeric_columns = {}
            # pop non-numeric columns
            all_columns = tuple(table.columns)
            for column in columns:
                if column not in table.columns:
                    raise ValueError
                col_index = all_columns.index(column)
                nonnumeric_columns[col_index] = (column, table.pop(column))
            # convert dataframes to int-dataframes
            int_df = table.applymap(replace_with_int)
            # convert df.dtypes to optimal
            int_df = int_df.convert_dtypes()
            # reinsert nonnumeric columns
            for nn_index, column in nonnumeric_columns.items():
                int_df.insert(nn_index, *column)
            # reset url_to_tables entry
            self.url_to_tables[urlpath][index] = int_df
