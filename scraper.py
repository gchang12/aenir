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
        table_url = urllib.parse.urljoin(self.home_url, path)
        response = r.get(table_url)
        response.raise_for_status()
        self.url_to_tables[path] = pd.read_html(response.text)

    def save_table(self, path: str):
        """
        Saves table data and junk.
        """
        pass

    def load_table(self, path: str):
        """
        Loads table data and junk
        """
        pass

if __name__ == '__main__':
    breakpoint()
