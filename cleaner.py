#!/usr/bin/python3
"""
Defines methods to clean up fields, null-rows, and non-int cells.
"""

import logging
import re
import json
from typing import Iterable
from collections import OrderedDict

import pandas as pd
from aenir.scraper import SerenesScraper

class SerenesCleaner(SerenesScraper):
    """
    Inherits: SerenesScraper.
    Defines methods for data cleanup process.
    """

    def __init__(self, game_num: int):
        """
        Defines filename to be manually filled
        for field cleanup process, in addition to parent
        attributes.
        """
        logging.info("\n__init__(self, %d, check_if_url_exists=False)", game_num)
        SerenesScraper.__init__(self, game_num, check_if_url_exists=False)
        self.fieldrecon_json = "fieldrecon.json"

    def replace_with_int_df(self, urlpath: str, columns: Iterable[str]):
        """
        Temporarily removes non-numeric columns.
        Converts numeric columns to those of the integer dtype.
        Reinserts non-numeric columns
        * Some tables within a urlpath may contain differing columns
        ** To use during finalization.
        Note: Does not raise an error even if non-numeric rows exist.
        """

        logging.info(
                "\nreplace_with_int_df(self, '%s', *%s)", urlpath, columns
                )

        def replace_with_int(cell: str) -> int:
            """
            Replaces a cell with itself cast to int.
            """
            new_cell = re.sub("[^0-9+-]*([-+]?[0-9]+).*", "\\1", cell)
            if re.fullmatch("[-+]?[0-9]+", new_cell):
                new_cell = int(new_cell)
            return new_cell

        nonnumeric_columns = OrderedDict()
        for index, table in enumerate(self.url_to_tables[urlpath]):
            logging.info("Converting self.url_to_tables['%s'][%d]...", urlpath, index)
            # original column set, for reference.
            table_columns = tuple(table.columns)
            # pop non-numeric columns
            for column in columns:
                if column not in table_columns:
                    self.url_to_tables[urlpath][index] = table.copy()
                    raise ValueError(f"{column} not a field in self.url_to_tables['{urlpath}'][%d]")
                col_index = table_columns.index(column)
                nonnumeric_columns[col_index] = (column, table.pop(column))
            # convert dataframes to int-dataframes
            try:
                int_df = table.applymap(replace_with_int)
            except TypeError as error:
                self.url_to_tables[urlpath][index] = table.copy()
                raise TypeError("Either not all nonnumeric columns were listed,"
                        "or this function has already been called.")
            # convert df.dtypes to optimal
            int_df = int_df.convert_dtypes()
            # reinsert nonnumeric columns
            for nn_index, column in nonnumeric_columns.items():
                int_df.insert(nn_index, *column)
            # reset url_to_tables entry
            nonnumeric_columns.clear()
            logging.info(
                    "Conversion successful. Setting self.url_to_tables['%s'][%d]", urlpath, index
                    )
            self.url_to_tables[urlpath][index] = int_df.convert_dtypes()

    def create_fieldrecon_file(self):
        """
        Compile a list of the unique fields in all compiled SQL tables.
        Save that list as a dict, mapping each value to None, to
        the filename indicated by the fieldrecon_json attribute.
        Save that dict to JSON, with indent=4.
        """
        logging.info("\ncreate_fieldrecon_file()")
        fieldname_set = set()
        if self.get_datafile_path(self.fieldrecon_json).exists():
            raise FileExistsError
        for tableset in self.url_to_tables.values():
            for table in tableset:
                fieldname_set.update(set(table.columns))
        fieldname_dict = {fieldname: None for fieldname in fieldname_set}
        json_file = str(self.get_datafile_path(self.fieldrecon_json))
        logging.info("Dumping field recon dict into JSON...")
        with open(json_file, mode='w', encoding='utf-8') as wfile:
            json.dump(fieldname_dict, wfile, indent=4)
        logging.info("Successfully dumped field recon dict into JSON...")

    def drop_nonnumeric_rows(self, urlpath: str, numeric_col: str = "Def"):
        """
        Takes a urlpath as an argument, and drops the non-numeric rows
        for all tables indicated by the urlpath.
        """
        logging.info("\ndrop_nonnumeric_rows('%s', numeric_col='%s')", urlpath, numeric_col)
        for index, table in enumerate(self.url_to_tables[urlpath]):
            logging.info("Dropping rows from table %d", index)
            self.url_to_tables[urlpath][index] = table[
                    pd.to_numeric(table[numeric_col], errors='coerce').notnull()
                    ]

    def apply_fieldrecon_file(self):
        """
        Applies fieldrecon dict mapping to fieldnames
        in all pd.DataFrame objects in url_to_tables.values()
        Raises ValueError if None is in the fieldrecon dict values.
        """
        logging.info("\napply_fieldrecon_file()")
        json_path = str(self.get_datafile_path(self.fieldrecon_json))
        with open(json_path, encoding='utf-8') as rfile:
            fielddict = json.load(rfile)
        if None in fielddict.values():
            raise ValueError("Null-value in dict.values. Terminating...")
        logging.info("Applying field recon mapping to all df's.")
        for tablelist in self.url_to_tables.values():
            for index, table in enumerate(tablelist):
                try:
                    tablelist[index] = table.rename(fielddict, axis=1).drop(columns="DROP")
                except KeyError:
                    tablelist[index] = table.rename(fielddict, axis=1)
        logging.info("Applied field recon mapping to all df's.")

if __name__ == "__main__":
    pass
