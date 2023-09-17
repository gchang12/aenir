#!/usr/bin/python3
"""
Defines the SerenesCleaner class.

SerenesCleaner: Defines methods to clean up table data.
"""

from typing import Tuple
import re
import json
import io
import logging

import pandas as pd

from aenir.transcriber import SerenesTranscriber

class SerenesCleaner(SerenesTranscriber):
    """
    Defines methods to clean tabular data.

    Parameters:
    - fieldrecon_file: File that stores the mapping of consolidated field names for all tables.
    - cls_recon_list: List of common arguments to pass to *_clsrecon_file methods.
    """

    def __init__(self, game_num: int):
        """
        Extends: SerenesTranscriber.__init__

        Parameters:
        - fieldrecon_file
        - cls_recon_list
        """
        SerenesTranscriber.__init__(self, game_num)
        self.fieldrecon_file = "fieldrecon.json"
        self.cls_recon_list = [
                (("characters/base-stats", "Name"), ("characters/growth-rates", "Name")),
                (("characters/base-stats", "Class"), ("classes/maximum-stats", "Class")),
                (("characters/base-stats", "Class"), ("classes/promotion-gains", "Class")),
                (("classes/promotion-gains", "Promotion"), ("classes/maximum-stats", "Class")),
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
        with open(fieldrecon_json, encoding='utf-8') as rfile:
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

    def create_clsrecon_file(self, ltable_columns: Tuple[str, str], rtable_columns: Tuple[str, str]):
        """
        Creates a mapping file for names in one table whose columns are not in another.

        Raises:
        - FileExistsError
        """
        # unpack variables
        ltable_url, fromcol_name = ltable_columns
        rtable_url, tocol_name = rtable_columns
        # map urlpaths to tablenames
        ltable_name = self.page_dict[ltable_url]
        rtable_name = self.page_dict[rtable_url]
        # create Path for write-destination
        clsrecon_json = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        if clsrecon_json.exists():
            raise FileExistsError
        # resultset := (SELECT ltable.iloc[0, :] WHERE ltable[fromcol] NOT IN rtable[tocol]);
        target_set = set()
        for rtable in self.url_to_tables[rtable_url]:
            target_set.update(set(rtable.loc[:, tocol_name]))
        clsrecon_dict = {}
        for ltable in self.url_to_tables[ltable_url]:
            clsrecon_dict.update(
                    {
                        primary_key: None for primary_key in
                        ltable[~ltable[fromcol_name].isin(target_set)].iloc[:, 0]
                        }
                    )
        # save: {result: null for result in resultset} |-> ltable-JOIN-rtable.json
        with io.open(str(clsrecon_json), mode="w", encoding="utf-8") as wfile:
            json.dump(clsrecon_dict, wfile, indent=4)
            logging.info("'%s' created.", str(clsrecon_json))

    def verify_clsrecon_file(self, ltable_url: str, rtable_columns: Tuple[str, str]):
        """
        Prints the mismatches in a given mapping-file as specified by arguments.
        """
        # unpack variables
        rtable_url, tocol_name = rtable_columns
        # map urlpaths to tablenames
        ltable_name = self.page_dict[ltable_url]
        rtable_name = self.page_dict[rtable_url]
        # create Path for write-destination
        clsrecon_json = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        with io.open(str(clsrecon_json), encoding='utf-8') as rfile:
            clsrecon_dict = json.load(rfile)
        # compile list of names to compare against
        rtable_set = set()
        for rtable in self.url_to_tables[rtable_url]:
            rtable_set.update(set(rtable.loc[:, tocol_name]))
        nomatch_set = set()
        for ltable in self.url_to_tables[ltable_url]:
            # check if ltable-values are in rtable_set
            for lkey in ltable.iloc[:, 0]:
                try:
                    if clsrecon_dict[lkey] is None or clsrecon_dict[lkey] in rtable_set:
                        continue
                    nomatch_set.add(lkey)
                except KeyError:
                    continue
        return nomatch_set

if __name__ == '__main__':
    pass
