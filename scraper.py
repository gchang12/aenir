#!/usr/bin/python3
"""
Fetches data tables off https://serenesforest.net/
Stores data tables into SQL databases.
"""

import logging
import urllib.parse

import requests as r
import pandas as pd


logging.basicConfig(level=logging.INFO)


class SerenesScraper:
    """
    Stores all parameters relevant to scraping process.
    Defines functions to scrape and save.
    """
    # URL_ROOT := {scheme://netloc}
    URL_ROOT = 'https://serenesforest.net/'
    def __init__(self, game_name: str):
        """
        Initialize:
        - home_url: Determines whence to begin scraping operations.
        - table_dict: section/page -> list[pd.DataFrame]
        """
        if not isinstance(game_name, str):
            raise TypeError
        logging.info("__init__(self, '%s');", game_name)
        self.game_name = game_name
        logging.info("self.game_name = '%s';", self.game_name)
        self.home_url = urllib.parse.urljoin(self.URL_ROOT, game_name)
        logging.info("self.home_url = '%s';", self.home_url)
        logging.info("response = requests.get(url=self.home_url);")
        response = r.get(self.home_url)
        logging.info("response.raise_for_status();")
        response.raise_for_status()
        logging.info("No exception was raised;")
        self.table_dict = {}
        logging.info("self.table_dict = {};")

    def scrape_tables(self, section: str, page: str):
        """
        Scrapes table objects from home_url/section/page.
        """
        for arg in (section, page):
            if not isinstance(arg, str):
                raise TypeError
        logging.info("self.scrape_tables(section='%s', page='%s');", section, page)
        table_url = urllib.parse.urljoin(self.home_url, section)
        table_url = urllib.parse.urljoin(table_url, page)
        logging.info("response = requests.get(url='%s');", table_url)
        response = r.get(table_url)
        logging.info("response.raise_for_status();")
        response.raise_for_status()
        logging.info("No exception was raised;")
        url_key = '_'.join([section, page])
        self.table_dict[url_key] = pd.read_html(response.text)
        logging.info("table_dict['%s'] = pd.read_html(response.text);", url_key)

if __name__ == '__main__':
    breakpoint()
