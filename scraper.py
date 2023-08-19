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
    PAGE_DICT = {
            "characters/base-stats": "characters__base_stats",
            "characters/growth-rates": "characters__growth_rates",
            "classes/maximum-stats": "classes__maximum_stats",
            "classes/promotion-gains": "classes__promotion_gains",
            }
    def __init__(self, game_num: int):
        """
        Initialize:
        - home_url: Determines whence to begin scraping operations.
        - url_to_tables: section/page -> list[pd.DataFrame]
        """
        logging.info("self.__init__(self, %d)", game_num)
        SerenesBase.__init__(self, game_num)
        logging.info("self.home_url = \"%s\"", self.home_url)
        self.home_url = "/".join((self.URL_ROOT, game_name))
        logging.info("requests.get(\"%s\")", self.home_url)
        response = r.get(self.home_url)
        logging.info("requests.raise_for_status(): Checking for errors")
        response.raise_for_status()
        logging.info("requests.raise_for_status(): OK")

    def scrape_tables(self, urlpath: str):
        """
        Scrapes table objects from HOME_URL/section/page.
        """
        if urlpath not in self.PAGE_DICT:
            logging.warning("'%s' not in self.PAGE_DICT", urlpath)
            raise ValueError
        table_url = "/".join([self.home_url, urlpath])
        logging.info("requests.get(\"%s\")", table_url)
        response = r.get(table_url)
        logging.info("requests.raise_for_status(): Checking for errors")
        response.raise_for_status()
        logging.info("requests.raise_for_status(): OK")
        logging.info("self.url_to_tables[\"%s\"] := list[pd.DataFrame]: Assigning", urlpath)
        self.url_to_tables[urlpath] = pd.read_html(response.text)
        logging.info("self.url_to_tables[\"%s\"] := list[pd.DataFrame]: OK", urlpath)

    def save_tables(self, urlpath: str):
        """
        Saves table data and junk.
        """
        tablename = self.page_dict[urlpath]
        tableindex = 0
        self.home_dir.mkdir(exist_ok=True, parents=True)
        logging.info("'%s' directory now exists.", str(self.home_dir))
        save_dir = str(self.home_dir.joinpath("raw_stats.db"))
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
        Loads table data and junk
        """
        save_dir = str(self.home_dir.joinpath("raw_stats.db"))
        tablename = self.PAGE_DICT[urlpath]
        self.url_to_tables[urlpath] = []
        tableindex = 0
        while True:
            table_name = tablename + str(tableindex)
            con = "sqlite:///" + save_dir
            logging.info("table = pd.read_sql_table%s", (table_name, con))
            try:
                table = pd.read_sql_table(table_name, con)
                tableindex += 1
                logging.info("Appending 'table' to self.url_tables[\"%s\"]", urlpath)
                self.url_to_tables[urlpath].append(table)
            except ValueError:
                logging.info("There were %d table(s) compiled for '%s'.", tableindex, tablename)
                break

if __name__ == '__main__':
    pass
