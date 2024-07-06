#!/usr/bin/python3
"""
Defines the SerenesTranscriber class.

SerenesTranscriber: Defines methods to save and load tables scraped from SF.net.
"""

from pathlib import Path
import logging

import pandas as pd

from aenir.scraper import SerenesScraper

class SerenesTranscriber(SerenesScraper):
    """
    Defines methods for IO-operations with respect to scraped tables.

    Parameters:
    - page_dict: Maps HTTP urlpath_s in SF.net to SQL table-names.
    - home_dir: Path object indicating the directory where all data is stored.
    - tables_file: The name of the database file that stores the scraped tables.
    """
    # list of default table-sets to scrape
    page_dict = {
        "characters/base-stats": "characters__base_stats",
        "characters/growth-rates": "characters__growth_rates",
        "classes/maximum-stats": "classes__maximum_stats",
        "classes/promotion-gains": "classes__promotion_gains",
    }

    def __init__(self, game_num: int):
        """
        Extends: SerenesScraper.__init__

        Defines parameters:
        - page_dict
        - home_dir
        - tables_file
        """
        SerenesScraper.__init__(self, game_num)
        self.home_dir = Path("data", self.game_name)
        self.tables_file = "raw_stats.db"

    def save_tables(self, urlpath: str):
        """
        Saves the table-list stored in url_to_tables[urlpath] to home_dir/tables_file.

        Raises:
        - ValueError: Table-list is empty.
        - TypeError: Table-list contains something other than a pd.DataFrame.
        Note: url_to_tables[urlpath] is deleted upon successful completion.
        """
        logging.info("SerenesTranscriber.save_tables(self, '%s')", urlpath)
        # add in checks here
        if not self.url_to_tables[urlpath]:
            # implicit: raise KeyError
            raise ValueError(f"SerenesTranscriber.url_to_tables['{urlpath}'] is empty. Aborting.")
        for table in self.url_to_tables[urlpath]:
            if type(table) == pd.DataFrame:
                continue
            raise TypeError(f"SerenesTranscriber.url_to_tables['{urlpath}'] contains a non-pd.Dataframe object. Aborting.")
        # real program starts here
        tablename = self.page_dict[urlpath]
        self.home_dir.mkdir(exist_ok=True, parents=True)
        save_file = str(self.home_dir.joinpath(self.tables_file))
        logging.info("Saving '%s' tables to '%s'.", urlpath, save_file)
        for tableindex, table in enumerate(self.url_to_tables[urlpath]):
            name = tablename + str(tableindex)
            con = "sqlite:///" + save_file
            logging.info("pd.DataFrame.to_sql(self, '%s', '%s', index=False)", name, con)
            table.to_sql(name, con, index=False)
            # add in try-except clause if the table exists?
        logging.info("del SerenesTranscriber.url_to_tables['%s']")
        del self.url_to_tables[urlpath]

    def load_tables(self, urlpath: str):
        """
        Loads the table-list into url_to_tables[urlpath] from home_dir/tables_file.

        Raises:
        - FileNotFoundError: tables_file does not exist.
        - KeyError: urlpath is not registered in page_dict.
        """
        logging.info("SerenesTranscriber.load_tables(self, '%s')", urlpath)
        load_path = self.home_dir.joinpath(self.tables_file)
        if not load_path.exists():
            raise FileNotFoundError(f"'{str(load_path)}' does not exist. Aborting.")
        load_file = str(load_path)
        tablename_root = self.page_dict[urlpath]
        logging.info("SerenesTranscriber.url_to_tables['%s'] = []", urlpath)
        self.url_to_tables[urlpath] = []
        tableindex = 0
        logging.info("Loading tables into SerenesTranscriber.url_to_tables['%s'].", urlpath)
        while True:
            table_name = tablename_root + str(tableindex)
            con = "sqlite:///" + load_file
            try:
                logging.info("pd.read_sql_table('%s', '%s')", table_name, con)
                table = pd.read_sql_table(table_name, con)
                tableindex += 1
                logging.info("SerenesTranscriber.url_to_tables['%s'].append(tables[%d])", urlpath, tableindex-1)
                self.url_to_tables[urlpath].append(table)
            except ValueError:
                logging.info("%d table(s) have been loaded into SerenesTranscriber.url_to_tables['%s']", tableindex, urlpath)
                break

    def get_urlname_from_tablename(self, tablename: str):
        """
        Defines a method to convert a SQL table-name to its HTTP urlpath equivalent.

        Raises:
        - AssertionError: The table-name does not have a urlpath equivalent.
        - AttributeError: tablename is not a string.
        """
        urlname = tablename.replace("__", "/").replace("_", "-")
        #!will raise AssertionError for invalid tablenames
        assert urlname in self.page_dict
        return urlname
