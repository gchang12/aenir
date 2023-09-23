#!/usr/bin/python3
"""
Defines the SerenesCleaner class.

SerenesCleaner: Defines methods to clean up table data.
"""

from typing import Tuple
import io
import re
import json
import logging

import pandas as pd

from aenir.transcriber import SerenesTranscriber

class SerenesCleaner(SerenesTranscriber):
    """
    Defines methods to clean tabular data.

    Parameters:
    - fieldrecon_file: File that stores the mapping of consolidated field names for all tables.
    - clsrecon_list: List of common arguments to pass to *_clsrecon_file methods.
    """

    def __init__(self, game_num: int):
        """
        Extends: SerenesTranscriber.__init__

        Parameters:
        - fieldrecon_file
        - clsrecon_list
        """
        SerenesTranscriber.__init__(self, game_num)
        self.fieldrecon_file = "fieldrecon.json"
        self.clsrecon_list = [
                (("characters/base-stats", "Name", "Name"), ("characters/growth-rates", "Name")),
                (("characters/base-stats", "Name", "Class"), ("classes/maximum-stats", "Class")),
                (("characters/base-stats", "Name", "Class"), ("classes/promotion-gains", "Class")),
                (("classes/promotion-gains", "Promotion", "Promotion"), ("classes/maximum-stats", "Class")),
                ]


    def drop_nonnumeric_rows(self, urlpath: str, numeric_col: str = "Def"):
        """
        Drops non-numeric rows in all tables mapped to the given urlpath.

        Identifies numeric column, which can be specified via option,
        filters to include rows containing non-numeric strings, and deletes those rows.
        """
        for index, table in enumerate(self.url_to_tables[urlpath]):
            logging.info("Dropping rows for table #%d of '%s'", index, urlpath)
            self.url_to_tables[urlpath][index] = table[
                    pd.to_numeric(table[numeric_col], errors='coerce').notnull()
                    ]

    def replace_with_int_df(self, urlpath: str):
        """
        Replaces each cell in a urlpath's tables with either itself or its numeric equivalent.
        """

        def replace_with_int(cell: str) -> int:
            """
            """
            # convert cell to str, then replace it with a numeric str
            new_cell = re.sub("[^0-9+-]*([-+]?[0-9]+).*", "\\1", str(cell))
            # if the cell is numeric, return the int-cast version
            if re.fullmatch("[-+]?[0-9]+", new_cell):
                return int(new_cell)
            # otherwise, return the original cell
            return cell

        for index, table in enumerate(self.url_to_tables[urlpath]):
            logging.info("Converting table#%d of '%s' to numeric.", index, urlpath)
            int_df = table.applymap(replace_with_int)
            self.url_to_tables[urlpath][index] = int_df.convert_dtypes()

    def create_fieldrecon_file(self):
        """
        Creates a JSON file to be referenced when mapping field names to a consistent standard.

        Raises:
        - FileExistsError: File exists.
        """
        fieldrecon_json = self.home_dir.joinpath(self.fieldrecon_file)
        if fieldrecon_json.exists():
            raise FileExistsError
        fieldname_set = set()
        for tableset in self.url_to_tables.values():
            for table in tableset:
                fieldname_set.update(set(table.columns))
        fieldname_dict = { fieldname: None for fieldname in fieldname_set }
        with open(str(fieldrecon_json), mode='w', encoding='utf-8') as wfile:
            json.dump(fieldname_dict, wfile, indent=4)
            logging.info("'%s' created.", str(fieldrecon_json))

    def apply_fieldrecon_file(self):
        """
        Renames the fields in all tables, and drops those that have been renamed to 'DROP!'.

        Raises:
        - FileNotFoundError: By io.open (implicit), when create_fieldrecon_file has not been called.
        - ValueError: Null-value is in the mapping-file.
        """
        fieldrecon_json = str(self.home_dir.joinpath(self.fieldrecon_file))
        with io.open(fieldrecon_json, encoding='utf-8') as rfile:
            fieldrecon_dict = json.load(rfile)
        if None in fieldrecon_dict.values():
            raise ValueError
        for urlpath, tablelist in self.url_to_tables.items():
            for index, table in enumerate(tablelist):
                try:
                    logging.info("Attempting to rename and drop columns for '%s'[%d].", urlpath, index)
                    tablelist[index] = table.rename(columns=fieldrecon_dict).drop(columns=["DROP!"])
                except KeyError:
                    logging.info("No columns to drop for '%s'[%d]. Renaming...", urlpath, index)
                    tablelist[index] = table.rename(columns=fieldrecon_dict)

    def create_clsrecon_file(self, ltable_args: Tuple[str, str, str], rtable_args: Tuple[str, str]):
        """
        """
        # unpack arguments
        ltable_url, lpkey, from_col = ltable_args
        rtable_url, to_col = rtable_args
        # compile names in to_col to see which names in from_col are not in the to_col
        rtable_nameset = set()
        for table in self.url_to_tables[rtable_url]:
            rtable_nameset.update(set(table.loc[:, to_col]))
        # map missing names to null, present names to themselves
        clsrecon_dict = {}
        for table in self.url_to_tables[ltable_url]:
            # get all names, map missing to None
            for pval, lrow in table.set_index(lpkey).iterrows():
                from_val = lrow.pop(from_col)
                if from_val not in rtable_nameset:
                    from_val = None
                clsrecon_dict[pval] = from_val
        # dump dict into file
        ltable_name = self.page_dict[ltable_url]
        rtable_name = self.page_dict[rtable_url]
        json_path = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        if json_path.exists():
            raise FileExistsError
        with open(str(json_path), encoding='utf-8') as wfile:
            json.dump(clsrecon_dict, wfile, indent=4)

    def verify_clsrecon_file(self, ltable_args: Tuple[str, str, str], rtable_args: Tuple[str, str]):
        """
        """
        # unpack arguments
        ltable_url, lpkey, from_col = ltable_args
        rtable_url, to_col = rtable_args
        # load clsrecon_dict
        ltable_name = self.page_dict[ltable_url]
        rtable_name = self.page_dict[rtable_url]
        json_path = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        with open(str(json_path), encoding='utf-8') as rfile:
            clsrecon_dict = json.load(rfile)
        # compile ltable pkey names
        ltable_nameset = set()
        for table in self.url_to_tables[ltable_url]:
            ltable_nameset.update(set(table.loc[:, lpkey]))
        # check difference; also, get better printing implementation
        print(f"Names in clsrecon_file, but not in {ltable_url} table(s).")
        print(set(clsrecon_dict) - ltable_nameset)
        # compile rtable values
        rtable_nameset = set()
        for table in self.url_to_tables[rtable_url]:
            rtable_nameset.update(set(table.loc[:, to_col]))
        # check difference
        ltable_valueset = set(clsrecon_dict.values())
        print(f"Values in clsrecon_file, but not in {rtable_url} table(s).")
        print((ltable_valueset - {None}) - rtable_nameset)

if __name__ == '__main__':
    pass
