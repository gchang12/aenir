#!/usr/bin/python3
"""
"""

import requests
import pandas as pd

from aenir._base import SerenesBase


class SerenesScraper(SerenesBase):
    """
    """

    def __init__(self, game_num: int):
        """
        """
        SerenesBase.__init__(self, game_num)
        # list of default table-sets to scrape
        self.page_dict = {
                "characters/base-stats": "characters__base_stats",
                "characters/growth-rates": "characters__growth_rates",
                "classes/maximum-stats": "classes__maximum_stats",
                "classes/promotion-gains": "classes__promotion_gains",
                }
        # stores the scraped tables
        self.url_to_tables = {}

    def scrape_tables(self, urlpath: str):
        """
        """
        #!will raise AssertionError if urlpath is not a str
        assert isinstance(urlpath, str)
        absolute_url = "/".join([self.URL_ROOT, self.game_name, urlpath])
        response = requests.get(absolute_url, timeout=1)
        #!will raise requests.exceptions.HTTPError if name does not exist
        response.raise_for_status()
        self.url_to_tables[urlpath] = pd.read_html(response.text)


if __name__ == '__main__':
    pass
