#!/usr/bin/python3
"""
Defines the SerenesScraper class.

SerenesScraper: Defines a single method for web-scraping SF.net.
"""

import logging

import requests
import pandas as pd

from aenir._base import SerenesBase


class SerenesScraper(SerenesBase):
    """
    Defines a scraper method, among other relevant parameters.

    Parameters:
    - url_to_tables: Stores the scraped tables in lists of pd.DataFrame_s.
    """

    def __init__(self, game_num: int):
        """
        Extends: SerenesBase.__init__

        Defines the following parameters:
        - page_dict: Maps urlpaths to SQL table names.
        - url_to_tables: Maps urlpaths to the tables contained in those urlpaths.
        """
        SerenesBase.__init__(self, game_num)
        # stores the scraped tables in lists of pd.DataFrame_s.
        self.url_to_tables = {}

    def scrape_tables(self, urlpath: str):
        """
        Maps url_to_tables[urlpath] to a list of tables obtained from web-scraping methods.
        """
        assert isinstance(urlpath, str)
        absolute_url = "/".join([self.URL_ROOT, self.game_name, urlpath])
        logging.info("Now scraping from '%s'...", absolute_url)
        response = requests.get(absolute_url, timeout=1)
        #!will raise requests.exceptions.HTTPError if name does not exist
        response.raise_for_status()
        logging.info("Scraping successful.")
        self.url_to_tables[urlpath] = pd.read_html(response.text)
        logging.info(
                "%d table(s) found, and loaded into url_to_tables['%s'].",
                len(self.url_to_tables[urlpath]), urlpath
                )


if __name__ == '__main__':
    pass
