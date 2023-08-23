#!/usr/bin/python3
"""
Fetches data tables off https://serenesforest.net/
Stores data tables into SQL databases, and loads them.
"""
# pylint: disable=W3101

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
        logging.info("self.__init__(self, %s)", game_num)
        SerenesBase.__init__(self, game_num)
        self._home_url = "/".join((self.URL_ROOT, self.game_name))
        logging.info("self.home_url = \"%s\"", self.home_url)
        if check_if_url_exists:
            logging.info("requests.get(\"%s\")", self.home_url)
            response = r.get(self.home_url)
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
        if not isinstance(urlpath, str):
            logging.warning("not isinstance('%s', str)", urlpath)
            raise TypeError
        table_url = "/".join([self.home_url, urlpath])
        logging.info("requests.get(\"%s\")", table_url)
        response = r.get(table_url)
        logging.info("requests.raise_for_status() # Checking for errors")
        response.raise_for_status()
        logging.info("requests.raise_for_status() # OK")
        logging.info("self.url_to_tables[\"%s\"] := list[pd.DataFrame]: Assigning", urlpath)
        self.url_to_tables[urlpath] = pd.read_html(response.text)
        logging.info("self.url_to_tables[\"%s\"] := list[pd.DataFrame]: OK", urlpath)

    def save_tables(self, urlpath: str, filename: str = "raw_stats.db"):
        """
        Saves pd.DataFrame tables to self.get_datafile_path(filename).
        Clears self.url_to_tables[urlpath] := list[pd.DataFrame].
        """
        tablename = self.page_dict[urlpath]
        tableindex = 0
        self.home_dir.mkdir(exist_ok=True, parents=True)
        logging.info("'%s' directory now exists.", str(self.home_dir))
        save_dir = str(self.home_dir.joinpath(filename))
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

    def load_tables(self, urlpath: str, filename: str = "raw_stats.db"):
        """
        Loads tables from self.get_datafile_path(filename).
        Stores tables as pd.DataFrame objects in
        self.url_to_tables[urlpath] := list[pd.DataFrame]
        """
        save_dir = str(self.home_dir.joinpath(filename))
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
