#!/usr/bin/python3
"""
"""

import logging

import requests as r
import pandas as pd

from aenir._base import SerenesBase

class SerenesScraper(SerenesBase):
    """
    """

    URL_ROOT = "https://serenesforest.net/"

    def __init__(self, game_num: int, check_if_url_exists=True):
        """
        """
        SerenesBase.__init__(self, game_num)
        self._home_url = "/".join((self.URL_ROOT, self.game_name))
        self.tables_file = "raw_stats.db"
        if check_if_url_exists:
            response = r.get(self.home_url, timeout=1)
            response.raise_for_status()

    @property
    def home_url(self):
        """
        """
        return self._home_url

    def scrape_tables(self, urlpath: str):
        """
        """
        if not isinstance(urlpath, str):
            raise TypeError
        table_url = "/".join([self.home_url, urlpath])
        response = r.get(table_url, timeout=1)
        response.raise_for_status()
        self.url_to_tables[urlpath] = pd.read_html(response.text)

    def save_tables(self, urlpath: str):
        """
        """
        tablename = self.page_dict[urlpath]
        tableindex = 0
        self.home_dir.mkdir(exist_ok=True, parents=True)
        save_dir = str(self.home_dir.joinpath(self.tables_file))
        while self.url_to_tables[urlpath]:
            table = self.url_to_tables[urlpath].pop(0)
            name = tablename + str(tableindex)
            con = "sqlite:///" + save_dir
            table.to_sql(name, con, index=False)
            tableindex += 1
        del self.url_to_tables[urlpath]

    def load_tables(self, urlpath: str):
        """
        """
        save_dir = str(self.home_dir.joinpath(self.tables_file))
        tablename_root = self.page_dict[urlpath]
        self.url_to_tables[urlpath] = []
        tableindex = 0
        while True:
            table_name = tablename_root + str(tableindex)
            con = "sqlite:///" + save_dir
            try:
                table = pd.read_sql_table(table_name, con)
                tableindex += 1
                self.url_to_tables[urlpath].append(table)
            except ValueError:
                break

if __name__ == '__main__':
    pass
