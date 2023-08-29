#!/usr/bin/python3
"""
Fetches data tables off https://serenesforest.net/
Stores data tables into SQL databases, and loads them.
"""

import logging

import requests as r
import pandas as pd

from aenir._base import SerenesBase

class SerenesScraper(SerenesBase):
    """
    Stores all parameters relevant to scraping process.
    Defines functions to scrape and save.
    """

    URL_ROOT = "https://serenesforest.net/"

    def __init__(self, game_num: int, check_if_url_exists=True):
        """
        Initialize:
        - home_url: Determines whence to begin scraping operations.
        - url_to_tables: section/page -> list[pd.DataFrame]
        """
        logging.info("\nself.__init__(self, %s)", game_num)
        SerenesBase.__init__(self, game_num)
        self._home_url = "/".join((self.URL_ROOT, self.game_name))
        logging.info("self.home_url = \"%s\"", self.home_url)
        self.tables_file = "raw_stats.db"
        if check_if_url_exists:
            logging.info("requests.get(\"%s\")", self.home_url)
            response = r.get(self.home_url, timeout=1)
            logging.info("requests.raise_for_status() # Checking for errors")
            response.raise_for_status()
            logging.info("requests.raise_for_status() # OK")

    @property
    def home_url(self):
        """
        Get:    str representing the online directory
                from which to extract data for the game.
        """
        return self._home_url

    def scrape_tables(self, urlpath: str):
        """
        Scrapes tables from HOME_URL/section/page.
        Tables are stored in self.url_to_tables[urlpath] list
        as pd.DataFrame objects.
        """
        logging.info("\nself.scrape_tables('%s')", urlpath)
        if not isinstance(urlpath, str):
            logging.warning("not isinstance('%s', str)", urlpath)
            raise TypeError
        table_url = "/".join([self.home_url, urlpath])
        logging.info("requests.get(\"%s\")", table_url)
        response = r.get(table_url, timeout=1)
        logging.info("requests.raise_for_status() # Checking for errors")
        response.raise_for_status()
        logging.info("requests.raise_for_status() # OK")
        logging.info("self.url_to_tables[\"%s\"] := list[pd.DataFrame]: Assigning", urlpath)
        self.url_to_tables[urlpath] = pd.read_html(response.text)
        logging.info("self.url_to_tables[\"%s\"] := list[pd.DataFrame]: OK", urlpath)

    def save_tables(self, urlpath: str):
        """
        Saves pd.DataFrame tables to self.get_datafile_path(self.tables_file).
        Clears self.url_to_tables[urlpath] := list[pd.DataFrame].
        """
        logging.info("\nself.save_tables('%s')", urlpath)
        tablename = self.page_dict[urlpath]
        tableindex = 0
        self.home_dir.mkdir(exist_ok=True, parents=True)
        logging.info("'%s' directory now exists.", str(self.home_dir))
        save_dir = str(self.home_dir.joinpath(self.tables_file))
        while self.url_to_tables[urlpath]:
            logging.info("table = self.url_to_tables[\"%s\"].pop(0)", urlpath)
            table = self.url_to_tables[urlpath].pop(0)
            name = tablename + str(tableindex)
            con = "sqlite:///" + save_dir
            logging.info("First row of '%s.%s': %s", self.game_name, name, table.head(n=1))
            table.to_sql(name, con, index=False)
            logging.info("table.to_sql(\"%s\", \"%s\", index=False)", name, con)
            tableindex += 1
        del self.url_to_tables[urlpath]
        logging.info("\"%s\" no longer in self.url_to_tables.", urlpath)

    def load_tables(self, urlpath: str):
        """
        Loads tables from self.get_datafile_path(self.tables_file).
        Stores tables as pd.DataFrame objects in
        self.url_to_tables[urlpath] := list[pd.DataFrame]
        """
        logging.info("\nself.load_tables('%s')", urlpath)
        save_dir = str(self.home_dir.joinpath(self.tables_file))
        tablename_root = self.page_dict[urlpath]
        self.url_to_tables[urlpath] = []
        tableindex = 0
        while True:
            table_name = tablename_root + str(tableindex)
            con = "sqlite:///" + save_dir
            logging.info("table = pd.read_sql_table%s", (table_name, con))
            try:
                table = pd.read_sql_table(table_name, con)
                tableindex += 1
                logging.info("Appending 'table' to self.url_tables[\"%s\"]", urlpath)
                self.url_to_tables[urlpath].append(table)
            except ValueError:
                logging.info("There were %d table(s) compiled for '%s'", tableindex, tablename_root)
                break

if __name__ == '__main__':
    pass
