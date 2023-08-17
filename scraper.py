#!/usr/bin/python3
"""
Fetches data tables off https://serenesforest.net/
Stores data tables into SQL databases.
"""

import logging
import urllib.parse

import requests as r
import pandas as pd

from _base import SerenesBase


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
            raise TypeError
        SerenesBase.__init__(self, game_name)
        self.home_url = urllib.parse.urljoin(self.URL_ROOT, game_name)
        response = r.get(self.home_url)
        response.raise_for_status()

    def scrape_tables(self, path: str):
        """
        Scrapes table objects from HOME_URL/section/page.
        """
        if not isinstance(path, str):
            raise TypeError
        table_url = "/".join([self.home_url, path])
        response = r.get(table_url)
        response.raise_for_status()
        self.url_to_tables[path] = pd.read_html(response.text)

    def save_tables(self, urlpath: str):
        """
        Saves table data and junk.
        """
        tablename = self.urlpath_to_tablename(urlpath)
        tableindex = 0
        self.home_dir.mkdir(exist_ok=True, parents=True)
        save_dir = self.home_dir.joinpath("raw_stats.db").__str__()
        while self.url_to_tables[urlpath]:
            table = self.url_to_tables[urlpath].pop(0)
            name = tablename + str(tableindex)
            con = "sqlite:///" + save_dir
            table.to_sql(name, con, index=False)
            tableindex += 1
        del self.url_to_tables[urlpath]

    def load_tables(self, tablename: str):
        """
        Loads table data and junk
        """
        save_dir = self.home_dir.joinpath("raw_stats.db").__str__()
        self.url_to_tables[self.tablename_to_urlpath(tablename)] = []
        tableindex = 0
        while True:
            table_name = tablename + str(tableindex)
            con = "sqlite:///" + save_dir
            try:
                table = pd.read_sql_table(table_name, con)
                self.url_to_tables[self.tablename_to_urlpath(tablename)].append(table)
                tableindex += 1
            except ValueError:
                break

if __name__ == '__main__':
    pass
