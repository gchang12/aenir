#!/usr/bin/python3
"""
"""

from pathlib import Path
import unittest

import pandas as pd

from aenir.transcriber import SerenesTranscriber


class TranscriberTest( unittest.TestCase ):
    """
    """

    def setUp( self ):
        """
        """
        self.sos_transcriber = SerenesTranscriber( 6 )
        self.sos_transcriber.tables_file = "MOCK-" + self.sos_transcriber.tables_file

    def tearDown( self ):
        """
        """
        absolute_tables_file = self.sos_transcriber.home_dir.joinpath(
                self.sos_transcriber.tables_file
                )
        absolute_tables_file.unlink( missing_ok=True )
        try:
            self.sos_transcriber.home_dir.rmdir()
            Path( "data" ).rmdir()
        except FileNotFoundError:
            pass

    def test_save_tables__failures( self ):
        """
        """
        urlpath = "characters/base-stats"
        # main: fails because there are no tables
        self.sos_transcriber.url_to_tables[ urlpath ] = []
        with self.assertRaises( ValueError ):
            self.sos_transcriber.save_tables( urlpath )
        # assert: url still in table-dict, data-dir DNE, tables-file DNE
        self.assertIn( urlpath, self.sos_transcriber.url_to_tables )
        self.assertFalse( Path("data").exists() )
        tables_file = self.sos_transcriber.tables_file
        self.assertFalse( self.sos_transcriber.home_dir.joinpath( tables_file ).exists() )
        # main: fails because not all values to be saved are pd.DataFrames
        self.sos_transcriber.url_to_tables[ urlpath ].append( None )
        self.sos_transcriber.url_to_tables[ urlpath ].append( pd.DataFrame() )
        with self.assertRaises( TypeError ):
            self.sos_transcriber.save_tables( urlpath )
        self.assertIn( urlpath, self.sos_transcriber.url_to_tables )
        self.assertFalse( Path("data").exists() )
        self.assertFalse( self.sos_transcriber.home_dir.joinpath( tables_file ).exists() )
        # main: fails because the urlpath is not registered
        self.sos_transcriber.url_to_tables.clear()
        with self.assertRaises( KeyError ):
            self.sos_transcriber.save_tables( urlpath )
        # urlpath was never in here to begin with
        #self.assertIn( urlpath, self.sos_transcriber.url_to_tables )
        self.assertFalse( Path("data").exists() )
        self.assertFalse( self.sos_transcriber.home_dir.joinpath( tables_file ).exists() )

    def test_saveload_tables( self ):
        """
        """
        urlpath = "characters/base-stats"
        # compile tables
        self.sos_transcriber.scrape_tables( urlpath )
        # save scraped table for comparison
        saved_bases = self.sos_transcriber.url_to_tables[ urlpath ][ 0 ].copy()
        # main:
        self.sos_transcriber.save_tables( urlpath )
        # urlpath is popped from url_to_tables
        self.assertNotIn( urlpath , self.sos_transcriber.url_to_tables )
        # data-dir should now exist
        self.assertTrue( self.sos_transcriber.home_dir.exists() )
        tables_file = self.sos_transcriber.tables_file
        # tables-file should now exist
        self.assertTrue( self.sos_transcriber.home_dir.joinpath( tables_file ).exists() )
        # main:
        self.sos_transcriber.load_tables( urlpath )
        self.assertIn( urlpath , self.sos_transcriber.url_to_tables )
        # before-table should match after-table
        loaded_bases = self.sos_transcriber.url_to_tables[ urlpath ][ 0 ]
        self.assertTrue( all( saved_bases == loaded_bases ) )

    def test_load_tables__failures( self ):
        """
        """
        urlpath = "characters/base-stats"
        # main: fails because file does not exist
        self.sos_transcriber.tables_file = "nonexistent_file"
        absolute_tables_file = self.sos_transcriber.home_dir.joinpath(
                self.sos_transcriber.tables_file
                )
        absolute_tables_file.unlink( missing_ok=True )
        self.assertFalse(
                self.sos_transcriber.home_dir.joinpath( self.sos_transcriber.tables_file ).exists()
                )
        self.sos_transcriber.url_to_tables[ urlpath ] = []
        # assert that url_to_tables contents remain the same
        old_urldict = self.sos_transcriber.url_to_tables.copy()
        old_tablelist = self.sos_transcriber.url_to_tables[ urlpath ].copy()
        with self.assertRaises( FileNotFoundError ):
            self.sos_transcriber.load_tables( urlpath )
        new_urldict = self.sos_transcriber.url_to_tables
        self.assertIn( urlpath , self.sos_transcriber.url_to_tables )
        new_tablelist = self.sos_transcriber.url_to_tables[ urlpath ]
        self.assertDictEqual( new_urldict , old_urldict )
        self.assertListEqual( old_tablelist , new_tablelist )

    def test_get_urlname( self ):
        """
        """
        # get registered urlname
        tablename = "characters__base_stats"
        # expected output
        expected = "characters/base-stats"
        # for developer's peace of mind
        self.assertIn( expected , self.sos_transcriber.page_dict )
        # main
        actual = self.sos_transcriber.get_urlname_from_tablename( tablename )
        self.assertEqual( actual , expected )

    def test_get_urlname__dne( self ):
        """
        """
        # non-registered urlname
        tablename = "characters__baked_fat"
        # expected output
        expected = "characters/baked-fat"
        # for developer's peace of mind
        self.assertNotIn( expected , self.sos_transcriber.page_dict )
        # main: fails by AssertionError
        with self.assertRaises( AssertionError ):
            actual = self.sos_transcriber.get_urlname_from_tablename( tablename )

if __name__ == '__main__':
    unittest.main()
