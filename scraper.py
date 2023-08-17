#!/usr/bin/python3
"""
Fetches data tables off https://serenesforest.net/
Stores data tables into SQL databases.
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
    def __init__(self, game_name: str):
        """
        Initialize:
        - home_url: Determines whence to begin scraping operations.
        - url_to_tables: section/page -> list[pd.DataFrame]
        """
        if not isinstance(game_name, str):
            logging.info("game_name='%s' is not a str.", game_name)
            raise TypeError
        SerenesBase.__init__(self, game_name)
        self.home_url = "/".join((self.URL_ROOT, game_name))
        logging.info("self.home_url = \"%s\"", self.home_url)
        logging.info("requests.get(\"%s\")", self.home_url)
        response = r.get(self.home_url)
        response.raise_for_status()
        logging.info("requests.raise_for_status(): No anomalies")

    def scrape_tables(self, path: str):
        """
        Scrapes table objects from HOME_URL/section/page.
        """
        if not isinstance(path, str):
            raise TypeError
        table_url = "/".join([self.home_url, path])
        response = r.get(table_url)
        logging.info("requests.get(\"%s\")", table_url)
        response.raise_for_status()
        logging.info("requests.raise_for_status(): No anomalies")
        self.url_to_tables[path] = pd.read_html(response.text)
        logging.info("self.url_to_tables[\"%s\"] := list[pd.DataFrame]", path)

    def save_tables(self, urlpath: str):
        """
        Saves table data and junk.
        """
        tablename = self.urlpath_to_tablename(urlpath)
        tableindex = 0
        self.home_dir.mkdir(exist_ok=True, parents=True)
        logging.info("'%s' directory now exists.", str(self.home_dir))
        save_dir = str(self.home_dir.joinpath("raw_stats.db"))
        while self.url_to_tables[urlpath]:
            table = self.url_to_tables[urlpath].pop(0)
            name = tablename + str(tableindex)
            con = "sqlite:///" + save_dir
            table.to_sql(name, con, index=False)
            logging.info("table.to_sql(\"%s\", \"%s\", index=False)", name, con)
            tableindex += 1
        del self.url_to_tables[urlpath]
        logging.info("\"%s\" no longer in self.url_to_tables.", urlpath)

    def load_tables(self, tablename: str):
        """
        Loads table data and junk
        """
        save_dir = str(self.home_dir.joinpath("raw_stats.db"))
        urlpath = self.tablename_to_urlpath(tablename)
        self.url_to_tables[urlpath] = []
        tableindex = 0
        while True:
            table_name = tablename + str(tableindex)
            con = "sqlite:///" + save_dir
            logging.info("table = pd.read_sql_table%s", (table_name, con))
            try:
                table = pd.read_sql_table(table_name, con)
                logging.info("Appending 'table' to self.url_tables[\"%s\"]", urlpath)
                self.url_to_tables[urlpath].append(table)
                tableindex += 1
            except ValueError:
                break

if __name__ == '__main__':
    pass
