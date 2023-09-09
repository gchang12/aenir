#!/usr/bin/python3
"""
"""

import logging
import re
import json
from typing import Iterable

import pandas as pd
from aenir.scraper import SerenesScraper

class SerenesCleaner(SerenesScraper):
    """
    """

    def __init__(self, game_num: int):
        """
        """
        SerenesScraper.__init__(self, game_num, check_if_url_exists=False)
        self.fieldrecon_json = "fieldrecon.json"

    def replace_with_int_df(self, urlpath: str, columns: Iterable[str] = []):
        """
        """


        def replace_with_int(cell: str) -> int:
            """
            """
            new_cell = re.sub("[^0-9+-]*([-+]?[0-9]+).*", "\\1", cell)
            if re.fullmatch("[-+]?[0-9]+", new_cell):
                new_cell = int(new_cell)
            return new_cell

        nonnumeric_columns = {}
        for index, table in enumerate(self.url_to_tables[urlpath]):
            table_columns = tuple(table.columns)
            table_copy = table.copy()
            for column in set(columns):
                if column not in table_columns:
                    self.url_to_tables[urlpath][index] = table_copy
                    raise ValueError(f"'{column}' not in the column-set of self.url_to_tables['{urlpath}'][{index}]")
                col_index = table_columns.index(column)
                nonnumeric_columns[col_index] = (column, table.pop(column))
            try:
                int_df = table.applymap(replace_with_int)
            except TypeError:
                self.url_to_tables[urlpath][index] = table_copy
                raise TypeError("Either not all nonnumeric columns were listed, "
                        "or this function has already been called.")
            int_df = int_df.convert_dtypes()
            for nn_index in sorted(nonnumeric_columns):
                column = nonnumeric_columns[nn_index]
                int_df.insert(nn_index, *column)
            nonnumeric_columns.clear()
            self.url_to_tables[urlpath][index] = int_df.convert_dtypes()

    def create_fieldrecon_file(self):
        """
        """
        fieldname_set = set()
        if self.get_datafile_path(self.fieldrecon_json).exists():
            raise FileExistsError
        for tableset in self.url_to_tables.values():
            for table in tableset:
                fieldname_set.update(set(table.columns))
        fieldname_dict = {fieldname: None for fieldname in fieldname_set}
        json_file = str(self.get_datafile_path(self.fieldrecon_json))
        with open(json_file, mode='w', encoding='utf-8') as wfile:
            json.dump(fieldname_dict, wfile, indent=4)

    def drop_nonnumeric_rows(self, urlpath: str, numeric_col: str = "Def"):
        """
        """
        for index, table in enumerate(self.url_to_tables[urlpath]):
            self.url_to_tables[urlpath][index] = table[
                    pd.to_numeric(table[numeric_col], errors='coerce').notnull()
                    ]

    def apply_fieldrecon_file(self):
        """
        """
        json_path = str(self.get_datafile_path(self.fieldrecon_json))
        with open(json_path, encoding='utf-8') as rfile:
            fielddict = json.load(rfile)
        if None in fielddict.values():
            raise ValueError("Null-value in dict.values. Terminating...")
        for tablelist in self.url_to_tables.values():
            for index, table in enumerate(tablelist):
                try:
                    tablelist[index] = table.rename(fielddict, axis=1).drop(columns="DROP")
                except KeyError:
                    tablelist[index] = table.rename(fielddict, axis=1)

if __name__ == "__main__":
    pass
