#!/usr/bin/python3
"""
Defines methods to clean up fields, null-rows, and non-int cells.
"""

import re
import json
from typing import List

import pandas as pd
from aenir.scraper import SerenesScraper

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

    def replace_with_int_df(self, urlpath: str, columns: List[str]):
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
            return new_cell

        for index, table in enumerate(self.url_to_tables[urlpath]):
            nonnumeric_columns = {}
            # original column set, for reference.
            table_columns = tuple(table.columns)
            # pop non-numeric columns
            for column in columns:
                if column not in table_columns:
                    raise ValueError
                col_index = table_columns.index(column)
                nonnumeric_columns[col_index] = (column, table.pop(column))
            # convert dataframes to int-dataframes
            int_df = table.applymap(replace_with_int)
            # convert df.dtypes to optimal
            #int_df = int_df.convert_dtypes()
            # reinsert nonnumeric columns
            for nn_index, column in nonnumeric_columns.items():
                int_df.insert(nn_index, *column)
            # reset url_to_tables entry
            self.url_to_tables[urlpath][index] = int_df

    def create_fieldrecon_file(self):
        """
        Compile a list of the unique fields in all compiled SQL tables.
        Save that list as a dict, mapping each value to None, to
        the filename indicated by the fieldrecon_json attribute.
        Save that dict to JSON, with indent=4.
        """
        fieldname_set = set()
        for tableset in self.url_to_tables.values():
            for table in tableset:
                fieldname_set.update(set(table.columns))
        fieldname_dict = {fieldname: None for fieldname in fieldname_set}
        json_file = str(self.get_datafile_path(self.fieldrecon_json))
        with open(json_file, mode='w', encoding='utf-') as wfile:
            json.dump(fieldname_dict, wfile, indent=4)

    def drop_nonnumeric_rows(self, urlpath: str, numeric_col: str = "HP"):
        """
        Takes a urlpath as an argument, and drops the non-numeric rows
        for all tables indicated by the urlpath.
        """
        for index, table in enumerate(self.url_to_tables[urlpath]):
            self.url_to_tables[urlpath][index] = table[
                    pd.to_numeric(table[numeric_col], errors='coerce').notnull()
                    ]

    def apply_fieldrecon_file(self):
        """
        Applies fieldrecon dict mapping to fieldnames
        in all pd.DataFrame objects in url_to_tables.values()
        Raises ValueError if None is in the fieldrecon dict values.
        """
        json_path = str(self.get_datafile_path(self.fieldrecon_json))
        with open(json_path, encoding='utf-8') as rfile:
            fielddict = json.load(rfile)
        if None in fielddict.values():
            raise ValueError
        for tablelist in self.url_to_tables.values():
            for index, table in enumerate(tablelist):
                tablelist[index] = table.rename(fielddict, axis=1)

if __name__ == "__main__":
    pass
