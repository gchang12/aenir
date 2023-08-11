#!/usr/bin/python3
"""
Fetches data tables off https://serenesforest.net/
Stores data tables into SQL databases.
"""

import logging
import typing
import urllib.parse

import requests as r
import pandas as pd


class SerenesScraper:
    """
    Stores all parameters relevant to scraping process.
    Defines functions to scrape and save.
    """
    # URL_ROOT := {scheme://netloc}
    URL_ROOT = 'https://serenesforest.net/'
    # Assert that the arguments are of specific types
    def __init__( self, path ):
        """
        Initialize:
        - home_url: Determines whence to begin scraping operations.
        - table_dict: section/page -> list[pd.DataFrame]
        """
        # Parameters and such -> DEBUG
        self.home_url = urllib.parse.urljoin( self.URL_ROOT, path )
        self.table_dict = {}

    def scrape_tables( self, section, page ):
        """
        Scrapes table objects from home_url/section/page.
        """
        # Operations -> INFO
        table_url = urllib.parse.urljoin( self.home_url, section )
        table_url = urllib.parse.urljoin( table_url, page )
        response = r.get( table_url )
        response.raise_for_status()
        self.table_dict[ '/'.join( [ section, page ] ) ] = pd.read_html( response.text )

if __name__ == '__main__':
    breakpoint()
