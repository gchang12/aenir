#!/usr/bin/python3
"""
Defines the ScraperTest class to test the aenir.SerenesScraper class.
"""

import unittest
import logging

import requests
import pandas as pd

from aenir.scraper import SerenesScraper

class ScraperTest(unittest.TestCase):
    """
    Defines tests for aenir.SerenesScraper.scrape_tables method.
    """

    def setUp(self):
        """
        Initializes SerenesScraper instance, and binds it to 'sos_scraper'.
        """
        # create Scraper instance
        self.sos_scraper = SerenesScraper(6)

    def test__init__attr(self):
        """
        Tests that 'URL_ROOT' is a property.
        """
        logging.info("ScraperTest.test_attr(self)")
        self.assertIn("URL_ROOT", dir(self.sos_scraper))
        with self.assertRaises(AttributeError):
            self.sos_scraper.URL_ROOT = None

    def test_scrape_tables__failures(self):
        """
        Initiates tests for all possible failures, and to assert that url_to_tables is unaffected.

        Failures identified:
        - urlpath is not a string.
        - urlpath is not valid
        """
        logging.info("ScraperTest.test_scrape_tables__failures(self)")
        # main: fails because argument is not a str
        with self.assertRaises(AssertionError):
            self.sos_scraper.scrape_tables(None)
        # affected parameters remain unchanged
        self.assertDictEqual({}, self.sos_scraper.url_to_tables)
        # main: fails because url is not found
        with self.assertRaises(requests.exceptions.HTTPError):
            self.sos_scraper.scrape_tables("characters/stuff")
        # affected parameters remain unchanged
        self.assertDictEqual({}, self.sos_scraper.url_to_tables)

    def test_scrape_tables(self):
        """
        Tests that the scraped tables are non-empty lists containing pd.DataFrame_s.

        The following conditions must be satisfied:
        - urlpath should exist in url_to_tables dict.
        - url_to_tables[urlpath] is a non-empty list of non-empty pd.DataFrame_s.
        """
        logging.info("ScraperTest.test_scrape_tables(self)")
        # scrape from this urlpath in {sf}/binding-blade
        urlpath = "characters/base-stats"
        # main
        self.sos_scraper.scrape_tables(urlpath)
        # urlpath has been added to url_to_tables dict
        self.assertIn(urlpath, self.sos_scraper.url_to_tables)
        # table collection is a non-empty list
        self.assertIsInstance(self.sos_scraper.url_to_tables[urlpath], list)
        self.assertNotEqual(self.sos_scraper.url_to_tables[urlpath], [])
        # table contents are non-empty pd.DataFrames
        for table in self.sos_scraper.url_to_tables[urlpath]:
            self.assertIsInstance(table, pd.DataFrame)
            self.assertFalse(table.empty)

if __name__ == '__main__':
    unittest.main()
