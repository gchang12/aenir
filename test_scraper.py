#!/usr/bin/python3

import unittest

import requests
import pandas as pd

from aenir.scraper import SerenesScraper

class ScraperTest( unittest.TestCase ):

    def setUp( self ):
        # create Scraper instance
        self.sos_scraper = SerenesScraper( 6 )

    def test_get_urlname( self ):
        # get registered urlname
        tablename = "characters__base_stats"
        # expected output
        expected = "characters/base-stats"
        # for developer's peace of mind
        self.assertIn( expected , self.sos_scraper.page_dict )
        # main
        actual = self.sos_scraper.get_urlname_from_tablename( tablename )
        self.assertEqual( actual , expected )

    def test_get_urlname__dne( self ):
        # non-registered urlname
        tablename = "characters__baked_fat"
        # expected output
        expected = "characters/baked-fat"
        # for developer's peace of mind
        self.assertNotIn( expected , self.sos_scraper.page_dict )
        # main: fails by AssertionError
        with self.assertRaises( AssertionError ):
            actual = self.sos_scraper.get_urlname_from_tablename( tablename )

    def test_scrape_tables__failures( self ):
        # main: fails because argument is not a str
        with self.assertRaises( AssertionError ):
            self.sos_scraper.scrape_tables( None )
        # affected parameters remain unchanged
        self.assertDictEqual( {} , self.sos_scraper.url_to_tables )
        # main: fails because url is not found
        with self.assertRaises( requests.exceptions.HTTPError ):
            self.sos_scraper.scrape_tables( "characters/stuff" )
        # affected parameters remain unchanged
        self.assertDictEqual( {} , self.sos_scraper.url_to_tables )

    def test_scrape_tables( self ):
        # scrape from this urlpath in {sf}/binding-blade
        urlpath = "characters/base-stats"
        # main
        self.sos_scraper.scrape_tables( urlpath )
        # urlpath has been added to url_to_tables dict
        self.assertIn( urlpath , self.sos_scraper.url_to_tables )
        # table collection is a list
        self.assertIsInstance( self.sos_scraper.url_to_tables[ urlpath ] , list )
        # table contents are non-empty pd.DataFrames
        for table in self.sos_scraper.url_to_tables [ urlpath ]:
            self.assertIsInstance( table , pd.DataFrame)
            self.assertFalse( table.empty )

if __name__ == '__main__':
    unittest.main()
