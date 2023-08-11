#!/usr/bin/python3
"""
Tests functionality of SerenesScraper methods
"""

import unittest
import requests as r

import pandas as pd

import scraper

class SerenesTestCase( unittest.TestCase ):
    """
    Tests that the methods defined in scraper.SerenesScraper work.
    """

    def setUp( self ):
        """
        Set up the scraper.SerenesScraper instance.
        """
        self.sos_scraper = scraper.SerenesScraper("binding-blade")

    def test_scrape_tables__path_notexists( self ):
        """
        Asserts that an error is raised if the path does not exist.
        No tables are appended to the 'table_dict'.
        """
        section_page = "characters", "accuracy"
        with self.assertRaises( r.exceptions.HTTPError ):
            no_name = self.sos_scraper.scrape_tables( *section_page )
        self.assertNotIn( '/'.join(section_page), self.sos_scraper.table_dict )
        with self.assertRaises( NameError ):
            del no_name

    def test_scrape_tables__path_exists( self ):
        """
        Asserts that the 'table_dict' object is appended
        with a list of pd.DataFrame objects.
        """
        section_page = ( "characters", "base-stats" )
        self.sos_scraper.scrape_tables( *section_page )
        url_key = '/'.join(section_page)
        self.assertIn( url_key, self.sos_scraper.table_dict )
        self.assertIsInstance( self.sos_scraper.table_dict[ url_key ], list)
        for table in self.sos_scraper.table_dict[ url_key ]:
            self.assertIsInstance( table, pd.DataFrame )

if __name__ == '__main__':
    unittest.main()
