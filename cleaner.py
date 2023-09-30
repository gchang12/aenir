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
        logging.info("SerenesCleaner.__init__(self, %d)", game_num)
        self.fieldrecon_file = "fieldrecon.json"
        self.clsrecon_list = [
                (("characters/base-stats", "Name", "Name"), ("characters/growth-rates", "Name")),
                (("characters/base-stats", "Name", "Class"), ("classes/maximum-stats", "Class")),
                (("characters/base-stats", "Name", "Class"), ("classes/promotion-gains", "Class")),
                (("classes/promotion-gains", "Promotion", "Promotion"), ("classes/maximum-stats", "Class")),
                (("classes/promotion-gains", "Promotion", "Promotion"), ("classes/promotion-gains", "Class")),
                ]


    def drop_nonnumeric_rows(self, urlpath: str, numeric_col: str = "Def"):
        """
        Drops non-numeric rows in all tables mapped to the given urlpath.

        Identifies numeric column, which can be specified via option,
        filters to include rows containing non-numeric strings, and deletes those rows.
        """
        logging.info("SerenesCleaner.drop_nonnumeric_rows(self, '%s', numeric_col='%s'", urlpath, numeric_col)
        for index, table in enumerate(self.url_to_tables[urlpath]):
            logging.info("Dropping rows in table '%s'.", self.page_dict[urlpath] + str(index))
            self.url_to_tables[urlpath][index] = table[
                    pd.to_numeric(table[numeric_col], errors='coerce').notnull()
                    ]

    def replace_with_int_df(self, urlpath: str):
        """
        Replaces each cell in a urlpath's tables with either itself or its numeric equivalent.
        """
        logging.info("SerenesCleaner.replace_with_int_df(self, '%s')", urlpath)

        def replace_with_int(cell: str) -> int:
            """
            Returns an object with its numeric equivalent; if none exists, returns the object itself.
            """
            # convert cell to str, then replace it with a numeric str
            new_cell = re.sub("[^0-9+-]*([-+]?[0-9]+).*", "\\1", str(cell))
            # if the cell is numeric, return the int-cast version
            if re.fullmatch("[-+]?[0-9]+", new_cell):
                return int(new_cell)
            # otherwise, return the original cell
            return cell

        for index, table in enumerate(self.url_to_tables[urlpath]):
            logging.info("Replacing '%s' with numeric equivalent.", self.page_dict[urlpath] + str(index))
            int_df = table.applymap(replace_with_int)
            self.url_to_tables[urlpath][index] = int_df.convert_dtypes()

    def create_fieldrecon_file(self):
        """
        Creates a JSON file to be referenced when mapping field names to a consistent standard.

        Raises:
        - FileExistsError: File exists.
        """
        logging.info("SerenesCleaner.create_fieldrecon_file(self)")
        fieldrecon_json = self.home_dir.joinpath(self.fieldrecon_file)
        if fieldrecon_json.exists():
            logging.warning("'%s' exists. Aborting.")
            raise FileExistsError
        fieldname_set = set()
        for tableset in self.url_to_tables.values():
            for table in tableset:
                fieldname_set.update(set(table.columns))
        fieldname_dict = {fieldname: None for fieldname in fieldname_set}
        logging.info("Saving fieldrecon_file to '%s'.", str(fieldrecon_json))
        with open(str(fieldrecon_json), mode='w', encoding='utf-8') as wfile:
            json.dump(fieldname_dict, wfile, indent=4)
            logging.info("'%s' saved successfully.", str(fieldrecon_json))

    def apply_fieldrecon_file(self):
        """
        Renames the fields in all tables, and drops those that have been renamed to 'DROP!'.

        Raises:
        - FileNotFoundError: By io.open (implicit), when create_fieldrecon_file has not been called.
        - ValueError: Null-value is in the mapping-file.
        """
        logging.info("SerenesCleaner.apply_fieldrecon_file(self)")
        fieldrecon_json = str(self.home_dir.joinpath(self.fieldrecon_file))
        logging.info("Loading '%s' into fieldrecon_dict.", fieldrecon_json)
        with io.open(fieldrecon_json, encoding='utf-8') as rfile:
            fieldrecon_dict = json.load(rfile)
        if None in fieldrecon_dict.values():
            logging.warning("Null-value found in fieldrecon_dict.values(). Aborting.")
            raise ValueError
        for urlpath, tablelist in self.url_to_tables.items():
            logging.info("Applying fieldrecon_file to tablelist := SerenesCleaner.url_to_tables['%s'].", urlpath)
            for index, table in enumerate(tablelist):
                logging.info("Renaming and dropping columns in tablelist[%d]", index)
                try:
                    tablelist[index] = table.rename(columns=fieldrecon_dict).drop(columns=["DROP!"])
                    logging.info("Columns renamed. 'DROP!' columns found, and successfully dropped.")
                except KeyError:
                    tablelist[index] = table.rename(columns=fieldrecon_dict)
                    logging.info("Columns renamed.")

    def create_clsrecon_file(self, ltable_args: Tuple[str, str, str], rtable_args: Tuple[str, str]):
        """
        Creates class-reconciliation dict for pseudo-foreign-key stat look-up.

        Raises:
        - FileExistsError
        - KeyError: Keys provided are invalid
        """
        logging.info("SerenesCleaner.create_clsrecon_file(self, %s, %s)", ltable_args, rtable_args)
        # unpack arguments
        ltable_url, lpkey, from_col = ltable_args
        rtable_url, to_col = rtable_args
        # compile names in to_col to see which names in from_col are not in the to_col
        rtable_nameset = set()
        logging.info("Compiling nameset for rtable_url := '%s'.", rtable_url)
        logging.info("pd.DataFrame.loc[:, '%s']", to_col)
        for table in self.url_to_tables[rtable_url]:
            rtable_nameset.update(set(table.loc[:, to_col]))
        # map missing names to null, present names to themselves
        clsrecon_dict = {}
        logging.info("Compiling clsrecon_dict for ltable_url := '%s'.", ltable_url)
        for table in self.url_to_tables[ltable_url]:
            # get all names, map missing to None
            for pval, lrow in table.set_index(lpkey).iterrows():
                # in case the from_col == pval
                try:
                    from_val = lrow.pop(from_col)
                except KeyError:
                    from_val = pval
                if from_val not in rtable_nameset:
                    from_val = None
                clsrecon_dict[pval] = from_val
                logging.info("clsrecon_dict['%s'] = '%s'", pval, from_val)
        # dump dict into file
        ltable_name = self.page_dict[ltable_url]
        rtable_name = self.page_dict[rtable_url]
        json_path = self.home_dir.joinpath(f"{ltable_name}-JOIN-{rtable_name}.json")
        if json_path.exists():
            logging.warning("'%s' exists. Aborting.")
            raise FileExistsError
        logging.info("Saving clsrecon_dict to '%s'.", str(json_path))
        with io.open(str(json_path), encoding='utf-8', mode='w') as wfile:
            json.dump(clsrecon_dict, wfile, indent=4)
            logging.info("'%s' has been saved successfully.", str(json_path))

if __name__ == '__main__':
    pass
